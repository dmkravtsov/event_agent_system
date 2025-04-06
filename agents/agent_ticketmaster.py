import requests
from datetime import datetime
from typing import Any, List
from base_agent import BaseAgent
from event_model import EventItem

class TicketmasterAgent(BaseAgent):
    name: str = "TicketmasterAgent"
    api_key: str = ""

    async def process(self, data: dict) -> List[EventItem]:
        try:
            self.api_key = data["api_key"]
            city = data["city"]
            start_datetime = data["start_datetime"]
            end_datetime = data["end_datetime"]
            size = data.get("size", 10)

            url = "https://app.ticketmaster.com/discovery/v2/events.json"
            params = {
                "apikey": self.api_key,
                "locale": "*",
                "city": city,
                "startDateTime": start_datetime,
                "endDateTime": end_datetime,
                "size": size
            }

            await self.log(f"Sending request to Ticketmaster API for city: {city}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            json_data = response.json()

            events = json_data.get('_embedded', {}).get('events', [])
            await self.log(f"Received {len(events)} events")

            return [self.parse_event(e) for e in events]

        except Exception as e:
            await self.handle_error(e, context=data)
            return []

    def parse_event(self, event: dict) -> EventItem:
        venue = event.get('_embedded', {}).get('venues', [{}])[0]
        classification = event.get('classifications', [{}])[0]
        images = event.get('images', [])

        return EventItem(
            title=event.get("name"),
            url=event.get("url"),
            start_date=datetime.strptime(
                event.get("dates", {}).get("start", {}).get("dateTime"),
                "%Y-%m-%dT%H:%M:%SZ"
            ) if event.get("dates", {}).get("start", {}).get("dateTime") else None,
            timezone=event.get("dates", {}).get("timezone"),
            city=venue.get("city", {}).get("name"),
            country=venue.get("country", {}).get("name"),
            venue=venue.get("name"),
            segment=classification.get("segment", {}).get("name"),
            genre=classification.get("genre", {}).get("name"),
            subgenre=classification.get("subGenre", {}).get("name"),
            latitude=float(venue.get("location", {}).get("latitude", 0)),
            longitude=float(venue.get("location", {}).get("longitude", 0)),
            image_url=images[0]["url"] if images else None,
            sales_start=datetime.fromisoformat(
                event.get("sales", {}).get("public", {}).get("startDateTime").replace("Z", "+00:00")
            ) if event.get("sales", {}).get("public", {}).get("startDateTime") else None,
            sales_end=datetime.fromisoformat(
                event.get("sales", {}).get("public", {}).get("endDateTime").replace("Z", "+00:00")
            ) if event.get("sales", {}).get("public", {}).get("endDateTime") else None,
            promoter=event.get("promoter", {}).get("name")
        )
