from datetime import date

import requests
from icalendar import Calendar, Event

url = "https://www.racedays.run/api/event"


def get_x_api_key():

    response = requests.get("https://www.racedays.run/events")
    [line] = [line for line in response.text.splitlines() if "__rdApiKey = " in line]
    x_api_key = line.split('"')[-2]

    return x_api_key


def build_ics(
    fname,
    x_api_key,
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

    data = requests.get(url, params=params, headers={"x-api-key": x_api_key}).json()

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


x_api_key = get_x_api_key()

build_ics("racedays.ics", x_api_key)
build_ics("unconfirmed-racedays.ics", x_api_key, confirmedDates=False)
build_ics(
    "oslo-racedays.ics",
    x_api_key,
    confirmedDates=True,
    minMeters=9999,
    latitude=59.91,
    longitude=10.74,
    radius=50,
)
