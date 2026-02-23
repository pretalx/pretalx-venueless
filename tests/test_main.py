from datetime import timedelta
from unittest.mock import patch

import pytest
import requests
from django.urls import reverse
from django.utils.timezone import now

from pretalx.cfp.signals import html_above_profile_page
from pretalx.schedule.signals import schedule_release

from pretalx_venueless.models import VenuelessSettings
from pretalx_venueless.venueless import push_to_venueless

SETTINGS_URL_NAME = "plugins:pretalx_venueless:settings"
CHECK_URL_NAME = "plugins:pretalx_venueless:check"
JOIN_URL_NAME = "plugins:pretalx_venueless:join"


@pytest.mark.django_db
def test_orga_can_access_settings(orga_client, event):
    response = orga_client.get(
        reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug}), follow=True
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_orga_can_save_settings(orga_client, event):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    with patch("pretalx_venueless.views.push_to_venueless") as mock_push:
        mock_push.return_value.raise_for_status.return_value = None
        response = orga_client.post(
            url,
            {"url": "https://venueless.example.com/", "token": "test-token"},
            follow=True,
        )
    assert response.status_code == 200
    settings = VenuelessSettings.objects.get(event=event)
    assert settings.url == "https://venueless.example.com/"
    assert settings.token == "test-token"


@pytest.mark.django_db
def test_orga_can_save_settings_with_join_link(orga_client, event):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    with patch("pretalx_venueless.views.push_to_venueless") as mock_push:
        mock_push.return_value.raise_for_status.return_value = None
        response = orga_client.post(
            url,
            {
                "url": "https://venueless.example.com/",
                "token": "test-token",
                "show_join_link": True,
                "join_url": "https://venueless.example.com/join",
                "secret": "secret-key",
                "issuer": "my-issuer",
                "audience": "my-audience",
            },
            follow=True,
        )
    assert response.status_code == 200
    settings = VenuelessSettings.objects.get(event=event)
    assert settings.show_join_link is True
    assert settings.secret == "secret-key"


@pytest.mark.django_db
def test_orga_save_join_link_without_required_fields(orga_client, event):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    with patch("pretalx_venueless.views.push_to_venueless") as mock_push:
        mock_push.return_value.raise_for_status.return_value = None
        response = orga_client.post(
            url,
            {
                "url": "https://venueless.example.com/",
                "token": "test-token",
                "show_join_link": True,
            },
        )
    assert response.status_code == 200
    assert response.context["form"].errors


@pytest.mark.django_db
def test_orga_save_with_push_error(orga_client, event):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    with patch("pretalx_venueless.views.push_to_venueless") as mock_push:
        mock_push.return_value.raise_for_status.side_effect = requests.ConnectionError(
            "Connection failed"
        )
        mock_push.return_value.text = "Connection failed"
        response = orga_client.post(
            url,
            {"url": "https://venueless.example.com/", "token": "test-token"},
            follow=True,
        )
    assert response.status_code == 200


@pytest.mark.django_db
def test_orga_save_with_return_url(orga_client, event):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    with patch("pretalx_venueless.views.push_to_venueless") as mock_push:
        mock_push.return_value.raise_for_status.return_value = None
        response = orga_client.post(
            url,
            {
                "url": "https://venueless.example.com/",
                "token": "test-token",
                "return_url": "https://venueless.example.com/admin",
            },
        )
    assert response.status_code == 302


@pytest.mark.django_db
def test_orga_settings_with_token_in_get(orga_client, event):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.get(
        url
        + "?token=initial-token&url=https://v.example.com/&returnUrl=https://v.example.com/admin"
    )
    assert response.status_code == 200
    assert response.context["connect_in_progress"]


@pytest.mark.django_db
def test_reviewer_cannot_access_settings(review_client, event):
    response = review_client.get(
        reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_check_endpoint_returns_200_for_enabled_plugin(client, event):
    response = client.get(reverse(CHECK_URL_NAME, kwargs={"event": event.slug}))
    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "*"


@pytest.mark.django_db
def test_check_endpoint_returns_404_for_missing_event(client):
    response = client.get(reverse(CHECK_URL_NAME, kwargs={"event": "nonexistent"}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_navbar_signal_for_orga(orga_client, event):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_can_join_property(event):
    settings = VenuelessSettings.objects.create(
        event=event,
        show_join_link=True,
        secret="s",
        issuer="i",
        audience="a",
        join_url="https://v.example.com/join",
    )
    assert settings.can_join is True


@pytest.mark.django_db
def test_can_join_property_with_future_start(event):
    settings = VenuelessSettings.objects.create(
        event=event,
        show_join_link=True,
        join_start=now() + timedelta(days=1),
        secret="s",
        issuer="i",
        audience="a",
        join_url="https://v.example.com/join",
    )
    assert settings.can_join is False


@pytest.mark.django_db
def test_can_join_property_disabled(event):
    settings = VenuelessSettings.objects.create(event=event, show_join_link=False)
    assert settings.can_join is False


@pytest.mark.django_db
def test_push_to_venueless_success(event):
    VenuelessSettings.objects.create(
        event=event, token="test-token", url="https://venueless.example.com/"
    )
    with patch("pretalx_venueless.venueless.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        response = push_to_venueless(event)
    assert response.status_code == 200
    mock_post.assert_called_once()


@pytest.mark.django_db
def test_push_to_venueless_failure(event):
    VenuelessSettings.objects.create(
        event=event, token="test-token", url="https://venueless.example.com/"
    )
    with patch("pretalx_venueless.venueless.requests.post") as mock_post:
        mock_post.return_value.status_code = 500
        response = push_to_venueless(event)
    assert response.status_code == 500


@pytest.mark.django_db
def test_schedule_release_signal(event):
    VenuelessSettings.objects.create(
        event=event, token="test-token", url="https://venueless.example.com/"
    )
    with patch("pretalx_venueless.signals.push_to_venueless") as mock_push:
        schedule_release.send(sender=event, schedule=None, user=None)
    mock_push.assert_called_once_with(event)


@pytest.mark.django_db
def test_schedule_release_signal_without_settings(event):
    with patch("pretalx_venueless.signals.push_to_venueless") as mock_push:
        schedule_release.send(sender=event, schedule=None, user=None)
    mock_push.assert_not_called()


@pytest.mark.django_db
def test_schedule_release_signal_without_url(event):
    VenuelessSettings.objects.create(event=event)
    with patch("pretalx_venueless.signals.push_to_venueless") as mock_push:
        schedule_release.send(sender=event, schedule=None, user=None)
    mock_push.assert_not_called()


@pytest.mark.django_db
def test_join_link_not_shown_for_anonymous(event, client, venueless_settings):
    results = html_above_profile_page.send(
        sender=event, request=client.get("/").wsgi_request
    )
    html_results = [r for _, r in results if r]
    assert not html_results


@pytest.mark.django_db
def test_join_endpoint_requires_auth(client, event):
    response = client.post(reverse(JOIN_URL_NAME, kwargs={"event": event.slug}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_join_endpoint_requires_speaker(orga_client, event, venueless_settings):
    response = orga_client.post(reverse(JOIN_URL_NAME, kwargs={"event": event.slug}))
    assert response.status_code == 403


@pytest.mark.django_db
def test_check_endpoint_disabled_plugin(client, event):
    event.disable_plugin("pretalx_venueless")
    event.save()
    response = client.get(reverse(CHECK_URL_NAME, kwargs={"event": event.slug}))
    assert response.status_code == 404
    event.enable_plugin("pretalx_venueless")
    event.save()
