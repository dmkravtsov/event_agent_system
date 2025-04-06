import logging
from serpapi import GoogleSearch
from typing import Any, List
from event_model import EventItem
from base_agent import BaseAgent
from datetime import datetime

class SerpApiAgent(BaseAgent):
    name: str = "SerpApiAgent"

    async def process(self, data: dict) -> List[EventItem]:
        await self.log(f"Sending request to SerpApi for city: {data['city']}")

        try:
            query_parts = ["events"]
            if data.get("keyword"):
                query_parts.append(data["keyword"])
            query_parts.append("in")
            query_parts.append(data["city"])
            query_parts.append(datetime.strptime(data["start_datetime"], "%Y-%m-%dT%H:%M:%SZ").strftime("%B %Y"))

            params = {
                "engine": "google_events",
                "q": " ".join(query_parts),
                "api_key": data["api_key"],
                "hl": "en",
                "gl": "us"
            }

            search = GoogleSearch(params)
            results = search.get_dict()
            events = results.get("events_results", [])

            parsed_events = []
            for event in events:
                raw_date = event.get("date", {}).get("start_date")
                start_date = None
                if raw_date:
                    try:
                        start_date = datetime.strptime(raw_date, "%Y-%m-%d")
                    except ValueError:
                        try:
                            start_date = datetime.strptime(raw_date, "%B %d, %Y")
                        except ValueError:
                            start_date = None

                item = EventItem(
                    title=event.get("title"),
                    url=event.get("link"),
                    start_date=start_date,
                    city=data["city"],
                    venue=event.get("venue", {}).get("name"),
                    country=None,
                    timezone=None,
                    genre=None,
                    segment=None,
                    subgenre=None,
                    latitude=None,
                    longitude=None,
                    image_url=None,
                    sales_start=None,
                    sales_end=None,
                    promoter=None
                )
                parsed_events.append(item)

            await self.log(f"Received {len(parsed_events)} events from SerpApi")
            return parsed_events

        except Exception as e:
            await self.handle_error(e, context=data)
            return []
