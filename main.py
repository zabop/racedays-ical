from datetime import date

import requests
from icalendar import Calendar, Event

url = "https://www.racedays.run/api/event"


def build_ics(
    fname,
    confirmedDates=True,
    minMeters=42196,
    latitude=None,
    longitude=None,
    radius=None,
):
    params = {
        "pageSize": 750,
        "pageNumber": 1,
        "from": "2026-07-30",
        "countryCode": "NO",
        "minMeters": minMeters,
        "includeWeeklyEvents": False,
        "includeCarousels": True,
        "onlyInternal": False,
        "confirmedDates": confirmedDates,
        "latitude": latitude,
        "longitude": longitude,
        "radius": radius,
    }

    data = requests.get(url, params=params).json()

    cal = Calendar()
    cal.add("prodid", "-//racedays-ical//EN")
    cal.add("version", "2.0")

    for item in data["data"]:
        event = Event()
        event.add("uid", item["id"])
        event.add("summary", item["name"])
        event.add("dtstart", date.fromisoformat(item["date"]))
        event.add("location", f'{item["location"]}, {item["country"]}')
        event.add("description", f'https://www.racedays.run/event/{item["slug"]}')
        cal.add_component(event)

    with open(fname, "wb") as f:
        f.write(cal.to_ical())

    print(f'Wrote {len(data["data"])} events to {fname}')


build_ics("racedays.ics")
build_ics("unconfirmed-racedays.ics", confirmedDates=False)
build_ics(
    "oslo-racedays.ics",
    confirmedDates=True,
    minMeters=9999,
    latitude=59.91,
    longitude=10.74,
    radius=50,
)
