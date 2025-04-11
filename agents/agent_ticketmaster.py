import requests
from datetime import datetime, timedelta
from typing import Any, List
from base_agent import BaseAgent
from event_model import EventItem


class TicketmasterAgent(BaseAgent):
    name: str = "TicketmasterAgent"
    api_key: str = ""

    async def process(self, data: dict) -> List[EventItem]:
        self.api_key = data["api_key"]
        city = data["city"]
        start_datetime = datetime.strptime(data["start_datetime"], "%Y-%m-%dT%H:%M:%SZ")
        end_datetime = datetime.strptime(data["end_datetime"], "%Y-%m-%dT%H:%M:%SZ")
        size = data.get("size", 100)
        max_pages = data.get("max_pages", 50)

        # Защита от превышения лимита Ticketmaster (1000 результатов)
        if size * max_pages > 1000:
            max_pages = 1000 // size

        url = "https://app.ticketmaster.com/discovery/v2/events.json"
        all_events = []

        # Разбивка диапазона на интервалы по 60 дней
        current = start_datetime
        while current < end_datetime:
            next_point = min(current + timedelta(days=60), end_datetime)

            for page in range(max_pages):
                params = {
                    "apikey": self.api_key,
                    "locale": "*",
                    "city": city,
                    "startDateTime": current.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "endDateTime": next_point.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "size": size,
                    "page": page
                }

                await self.log(f"Requesting Ticketmaster page {page} for {city} | {params['startDateTime']} → {params['endDateTime']}")
                response = requests.get(url, params=params)
                if response.status_code == 404:
                    break

                response.raise_for_status()
                json_data = response.json()

                events = json_data.get('_embedded', {}).get('events', [])
                if not events:
                    break

                for event in events:
                    all_events.append(self.parse_event(event))

                total_pages = json_data.get('page', {}).get('totalPages', 1)
                if page + 1 >= total_pages:
                    break

            current = next_point

        await self.log(f"Parsed total {len(all_events)} events from Ticketmaster")
        return all_events

    def parse_event(self, event: dict) -> EventItem:
        venue = event.get('_embedded', {}).get('venues', [{}])[0]
        classification = event.get('classifications', [{}])[0]
        images = event.get('images', [])

        return EventItem(
            source_id=event.get("id"),
            title=event.get("name"),
            url=event.get("url"),
            start_date=datetime.strptime(
                event.get("dates", {}).get("start", {}).get("dateTime"),
                "%Y-%m-%dT%H:%M:%SZ"
            ) if event.get("dates", {}).get("start", {}).get("dateTime") else None,
            sales_start=datetime.fromisoformat(
                event.get("sales", {}).get("public", {}).get("startDateTime").replace("Z", "+00:00")
            ) if event.get("sales", {}).get("public", {}).get("startDateTime") else None,
            sales_end=datetime.fromisoformat(
                event.get("sales", {}).get("public", {}).get("endDateTime").replace("Z", "+00:00")
            ) if event.get("sales", {}).get("public", {}).get("endDateTime") else None,
            duration_seconds=None,
            timezone=event.get("dates", {}).get("timezone"),
            city=venue.get("city", {}).get("name"),
            country=venue.get("country", {}).get("name"),
            venue=venue.get("name"),
            latitude=float(venue.get("location", {}).get("latitude", 0)),
            longitude=float(venue.get("location", {}).get("longitude", 0)),
            segment=classification.get("segment", {}).get("name"),
            genre=classification.get("genre", {}).get("name"),
            subgenre=classification.get("subGenre", {}).get("name"),
            category="theatre",
            labels=["theatre"],
            promoter=event.get("promoter", {}).get("name") if event.get("promoter") else None,
            attendance=None,
            predicted_spend=None,
            description=None,
            image_urls=[img.get("url") for img in images if img.get("url")],
            ticket_urls=[event.get("url")] if event.get("url") else None,
            price=None
        )


# import requests
# from datetime import datetime
# from typing import Any, List
# from base_agent import BaseAgent
# from event_model import EventItem


# class TicketmasterAgent(BaseAgent):
#     name: str = "TicketmasterAgent"
#     api_key: str = ""

#     async def process(self, data: dict) -> List[EventItem]:
#         self.api_key = data["api_key"]
#         city = data["city"]
#         start_datetime = data["start_datetime"]
#         end_datetime = data["end_datetime"]
#         size = data.get("size", 1)
#         max_pages = data.get("max_pages", 1)

#         url = "https://app.ticketmaster.com/discovery/v2/events.json"

#         all_events = []
#         page = 0

#         while page < max_pages:
#             params = {
#                 "apikey": self.api_key,
#                 "locale": "*",
#                 "city": city,
#                 "startDateTime": start_datetime,
#                 "endDateTime": end_datetime,
#                 "size": size,
#                 "page": page
#             }

#             await self.log(f"Requesting Ticketmaster page {page} for city: {city}")
#             response = requests.get(url, params=params)
#             if response.status_code == 404:
#                 break  # больше страниц нет

#             response.raise_for_status()
#             json_data = response.json()

#             events = json_data.get('_embedded', {}).get('events', [])
#             if not events:
#                 break

#             for event in events:
#                 all_events.append(self.parse_event(event))

#             page += 1
#             total_pages = json_data.get('page', {}).get('totalPages', 1)
#             if page >= total_pages:
#                 break

#         await self.log(f"Parsed total {len(all_events)} events from Ticketmaster")
#         return all_events

#     def parse_event(self, event: dict) -> EventItem:
#         venue = event.get('_embedded', {}).get('venues', [{}])[0]
#         classification = event.get('classifications', [{}])[0]
#         images = event.get('images', [])

#         return EventItem(
#             source_id=event.get("id"),
#             title=event.get("name"),
#             url=event.get("url"),
#             start_date=datetime.strptime(
#                 event.get("dates", {}).get("start", {}).get("dateTime"),
#                 "%Y-%m-%dT%H:%M:%SZ"
#             ) if event.get("dates", {}).get("start", {}).get("dateTime") else None,
#             sales_start=datetime.fromisoformat(
#                 event.get("sales", {}).get("public", {}).get("startDateTime").replace("Z", "+00:00")
#             ) if event.get("sales", {}).get("public", {}).get("startDateTime") else None,
#             sales_end=datetime.fromisoformat(
#                 event.get("sales", {}).get("public", {}).get("endDateTime").replace("Z", "+00:00")
#             ) if event.get("sales", {}).get("public", {}).get("endDateTime") else None,
#             duration_seconds=None,
#             timezone=event.get("dates", {}).get("timezone"),
#             city=venue.get("city", {}).get("name"),
#             country=venue.get("country", {}).get("name"),
#             venue=venue.get("name"),
#             latitude=float(venue.get("location", {}).get("latitude", 0)),
#             longitude=float(venue.get("location", {}).get("longitude", 0)),
#             segment=classification.get("segment", {}).get("name"),
#             genre=classification.get("genre", {}).get("name"),
#             subgenre=classification.get("subGenre", {}).get("name"),
#             category="theatre",
#             labels=["theatre"],
#             promoter=event.get("promoter", {}).get("name") if event.get("promoter") else None,
#             attendance=None,
#             predicted_spend=None,
#             description=None,
#             image_urls=[img.get("url") for img in images if img.get("url")],
#             ticket_urls=[event.get("url")] if event.get("url") else None,
#             price=None
#         )




# import requests
# from datetime import datetime
# from typing import Any, List
# from base_agent import BaseAgent
# from event_model import EventItem

# class TicketmasterAgent(BaseAgent):
#     name: str = "TicketmasterAgent"
#     api_key: str = ""

#     async def process(self, data: dict) -> List[EventItem]:
#         try:
#             self.api_key = data["api_key"]
#             city = data["city"]
#             start_datetime = data["start_datetime"]
#             end_datetime = data["end_datetime"]
#             size = data.get("size", 10)

#             url = "https://app.ticketmaster.com/discovery/v2/events.json"
#             params = {
#                 "apikey": self.api_key,
#                 "locale": "*",
#                 "city": city,
#                 "startDateTime": start_datetime,
#                 "endDateTime": end_datetime,
#                 "size": size
#             }

#             await self.log(f"Sending request to Ticketmaster API for city: {city}")
#             response = requests.get(url, params=params)
#             response.raise_for_status()
#             json_data = response.json()

#             events = json_data.get('_embedded', {}).get('events', [])
#             await self.log(f"Received {len(events)} events")

#             return [self.parse_event(e) for e in events]

#         except Exception as e:
#             await self.handle_error(e, context=data)
#             return []

#     def parse_event(self, event: dict) -> EventItem:
#         venue = event.get('_embedded', {}).get('venues', [{}])[0]
#         classification = event.get('classifications', [{}])[0]
#         images = event.get('images', [])

#         return EventItem(
#             title=event.get("name"),
#             url=event.get("url"),
#             start_date=datetime.strptime(
#                 event.get("dates", {}).get("start", {}).get("dateTime"),
#                 "%Y-%m-%dT%H:%M:%SZ"
#             ) if event.get("dates", {}).get("start", {}).get("dateTime") else None,
#             timezone=event.get("dates", {}).get("timezone"),
#             city=venue.get("city", {}).get("name"),
#             country=venue.get("country", {}).get("name"),
#             venue=venue.get("name"),
#             segment=classification.get("segment", {}).get("name"),
#             genre=classification.get("genre", {}).get("name"),
#             subgenre=classification.get("subGenre", {}).get("name"),
#             latitude=float(venue.get("location", {}).get("latitude", 0)),
#             longitude=float(venue.get("location", {}).get("longitude", 0)),
#             image_url=images[0]["url"] if images else None,
#             sales_start=datetime.fromisoformat(
#                 event.get("sales", {}).get("public", {}).get("startDateTime").replace("Z", "+00:00")
#             ) if event.get("sales", {}).get("public", {}).get("startDateTime") else None,
#             sales_end=datetime.fromisoformat(
#                 event.get("sales", {}).get("public", {}).get("endDateTime").replace("Z", "+00:00")
#             ) if event.get("sales", {}).get("public", {}).get("endDateTime") else None,
#             promoter=event.get("promoter", {}).get("name")
#         )
