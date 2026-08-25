import asyncio
import os
from datetime import datetime, timezone

from icalendar import Calendar, Event
from spond import spond

username = os.environ["SPOND_USERNAME"]
password = os.environ["SPOND_PASSWORD"]
# Group UID (the API wants this, not the "OXHST" invite code)
group_id = os.environ["SPOND_GROUP_ID"]


class SyncSpond:
    def __init__(self, username, password):
        self._loop = asyncio.new_event_loop()

        # Spond() builds an aiohttp ClientSession/CookieJar in __init__, which
        # needs a running loop, so construct it inside our loop.
        async def _make():
            return spond.Spond(username=username, password=password)

        self._spond = self._run(_make())

    def _run(self, coro):
        return self._loop.run_until_complete(coro)

    def get_events(self, **kwargs):
        return self._run(self._spond.get_events(**kwargs)) or []

    def close(self):
        if self._spond.clientsession:
            self._run(self._spond.clientsession.close())
        self._loop.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def get_all_events(s, group_id):
    """Every event of the group, past and future, oldest first."""
    return sorted(
        s.get_events(
            group_id=group_id,
            include_scheduled=True,
            include_hidden=True,
            min_start=datetime(2000, 1, 1, tzinfo=timezone.utc),
            max_start=datetime(2100, 1, 1, tzinfo=timezone.utc),
            max_events=1000,
        ),
        key=lambda e: e["startTimestamp"],
    )


def build_ics(fname, events):
    cal = Calendar()
    cal.add("prodid", "-//racedays-ical//spond//EN")
    cal.add("version", "2.0")

    for item in events:
        event = Event()
        event.add("uid", item["id"])
        event.add("summary", item["heading"])
        event.add("dtstart", datetime.fromisoformat(item["startTimestamp"]))
        event.add("dtend", datetime.fromisoformat(item["endTimestamp"]))
        if item.get("description"):
            event.add("description", item["description"])
        location = item.get("location") or {}
        place = ", ".join(
            p for p in (location.get("feature"), location.get("address")) if p
        )
        if place:
            event.add("location", place)
        cal.add_component(event)

    with open(fname, "wb") as f:
        f.write(cal.to_ical())

    print(f"Wrote {len(events)} events to {fname}")


with SyncSpond(username, password) as s:
    build_ics("spond.ics", get_all_events(s, group_id))
