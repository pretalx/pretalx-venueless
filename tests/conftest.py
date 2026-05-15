import datetime as dt

import pytest
from django.core import management
from django_scopes import scopes_disabled

from pretalx.event.domain.event import initialise_event
from pretalx.event.domain.plugins import enable_plugin
from pretalx.event.models import Event, Organiser, Team
from pretalx.person.models import SpeakerProfile, User
from pretalx.schedule.domain.release import freeze_schedule
from pretalx.schedule.models import Room, TalkSlot
from pretalx.submission.models import Submission, SubmissionType
from pretalx.submission.models.submission import SpeakerRole

from pretalx_venueless.models import VenuelessSettings


@pytest.fixture(scope="session", autouse=True)
def collect_static(request):
    management.call_command("collectstatic", "--noinput", "--clear")


@pytest.fixture
def organiser():
    with scopes_disabled():
        o = Organiser.objects.create(name="Super Organiser", slug="superorganiser")
        Team.objects.create(
            name="Organisers",
            organiser=o,
            can_create_events=True,
            can_change_teams=True,
            can_change_organiser_settings=True,
            can_change_event_settings=True,
            can_change_submissions=True,
        )
        Team.objects.create(name="Reviewers", organiser=o, is_reviewer=True)
    return o


@pytest.fixture
def event(organiser):
    today = dt.date.today()
    with scopes_disabled():
        event = Event.objects.create(
            name="Fancy testevent",
            is_public=True,
            slug="test",
            email="orga@orga.org",
            date_from=today,
            date_to=today + dt.timedelta(days=3),
            organiser=organiser,
        )
        initialise_event(event)
        enable_plugin(event, "pretalx_venueless")
        event.save()
        for team in organiser.teams.all():
            team.limit_events.add(event)
    return event


@pytest.fixture
def orga_user(event):
    with scopes_disabled():
        user = User.objects.create_user(
            password="orgapassw0rd", email="orgauser@orga.org", name="Orga User"
        )
        team = event.organiser.teams.filter(
            can_change_organiser_settings=True, is_reviewer=False
        ).first()
        team.members.add(user)
        team.save()
    return user


@pytest.fixture
def review_user(event):
    with scopes_disabled():
        user = User.objects.create_user(
            password="reviewpassw0rd", email="reviewuser@orga.org", name="Review User"
        )
        team = event.organiser.teams.filter(
            can_change_organiser_settings=False, is_reviewer=True
        ).first()
        team.members.add(user)
        team.save()
    return user


@pytest.fixture
def orga_client(orga_user, client):
    client.force_login(orga_user)
    return client


@pytest.fixture
def review_client(review_user, client):
    client.force_login(review_user)
    return client


@pytest.fixture
def venueless_settings(event):
    settings, _ = VenuelessSettings.objects.get_or_create(
        event=event,
        defaults={
            "token": "test-token-123",
            "url": "https://venueless.example.com/",
            "secret": "test-secret",
            "issuer": "test-issuer",
            "audience": "test-audience",
            "join_url": "https://venueless.example.com/join",
            "show_join_link": True,
        },
    )
    return settings


@pytest.fixture
def speaker(event):
    with scopes_disabled():
        user = User.objects.create_user(
            password="speakerpassw0rd", email="speaker@example.org", name="Test Speaker"
        )
        speaker_profile = SpeakerProfile.objects.create(user=user, event=event)
        submission_type = SubmissionType.objects.filter(event=event).first()
        if not submission_type:
            submission_type = SubmissionType.objects.create(
                event=event, name="Talk", default_duration=30
            )
        submission = Submission.objects.create(
            event=event,
            title="Test Talk",
            submission_type=submission_type,
            state="confirmed",
        )
        SpeakerRole.objects.create(
            submission=submission, speaker=speaker_profile, position=0
        )
    return speaker_profile


@pytest.fixture
def speaker_client(speaker, client):
    client.force_login(speaker.user)
    return client


@pytest.fixture
def released_speaker(speaker, event):
    """A speaker whose talk is in a released schedule, so the speaker is
    visible in event.speakers and event.talks."""
    with scopes_disabled():
        submission = speaker.submissions.filter(event=event).first()
        room = Room.objects.create(event=event, name="Room 1")
        TalkSlot.objects.create(
            submission=submission,
            schedule=event.wip_schedule,
            room=room,
            start=event.datetime_from,
            end=event.datetime_from + dt.timedelta(hours=1),
            is_visible=True,
        )
        freeze_schedule(event.wip_schedule, "v1", notify_speakers=False)
    return speaker


@pytest.fixture
def released_speaker_client(released_speaker, client):
    client.force_login(released_speaker.user)
    return client
