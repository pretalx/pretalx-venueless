import datetime as dt

from django.dispatch import receiver
from django.urls import resolve, reverse
from django.utils.translation import ugettext_lazy as _
from pretalx.common.models.settings import hierarkey
from pretalx.orga.signals import nav_event_settings
from pretalx.schedule.signals import schedule_release

from .venueless import push_to_venueless

hierarkey.add_type("venueless_last_push", None, dt.datetime)


@receiver(schedule_release, dispatch_uid="venuless_schedule_release")
def on_schedule_release(event, schedule, user, **kwargs):
    if not (event.settings.venueless_url and event.settings.venueless_token):
        return
    push_to_venueless()


@receiver(nav_event_settings, dispatch_uid="venueless_nav_settings")
def navbar_info(sender, request, **kwargs):
    url = resolve(request.path_info)

    if not request.user.has_perm("orga.change_settings", request.event):
        return []

    return [
        {
            "label": _("Venueless"),
            "url": reverse(
                "plugins:pretalx_venueless:settings",
                kwargs={
                    "event": request.event.slug,
                },
            ),
            "active": url.namespace == "plugins:pretalx_venueless"
            and url.url_name == "settings",
        }
    ]
