from urllib.parse import urljoin

import urllib3
from django.conf import settings
from django.utils.timezone import now

from .models import VenuelessSettings


def push_to_venueless(event, venueless_settings=None):
    if venueless_settings is None:
        venueless_settings = VenuelessSettings.for_event(event)
    url = urljoin(venueless_settings.url, "schedule_update")
    token = venueless_settings.token
    response = urllib3.request(
        "POST",
        url,
        json={"domain": event.custom_domain or settings.SITE_URL, "event": event.slug},
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    if response.status == 200:
        venueless_settings.last_push = now()
        venueless_settings.save(update_fields=["last_push"])
    return response
