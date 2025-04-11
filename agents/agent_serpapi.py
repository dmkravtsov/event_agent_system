
import logging
from serpapi import GoogleSearch
from typing import Any, List
from event_model import EventItem
from base_agent import BaseAgent
from datetime import datetime, timezone
from dateutil.parser import parse as parse_date


class SerpApiAgent(BaseAgent):
    name: str = "SerpApiAgent"

    async def process(self, data: dict) -> List[EventItem]:
        await self.log(f"Sending request to SerpApi for city: {data['city']}")

        start_dt = parse_date(data["start_datetime"])
        end_dt = parse_date(data["end_datetime"])
        api_key = data["api_key"]
        city = data["city"]
        keyword = data.get("keyword", "")
        max_pages = 10  # жёстко задаём 10 запросов
        size = 20       # жёстко задаём по 20 результатов

        query_parts = ["events"]
        if keyword and keyword.strip().lower() != "event":
            query_parts.append(keyword)
        query_parts.append("in")
        query_parts.append(city)

        base_params = {
            "engine": "google_events",
            "q": " ".join(query_parts),
            "api_key": api_key,
            "hl": "en",
            "gl": "us"
        }

        parsed_events = []
        seen_keys = set()

        for i in range(max_pages):
            start_index = i * size
            params = base_params.copy()
            params["start"] = start_index
            search = GoogleSearch(params)
            results = search.get_dict()
            events = results.get("events_results", [])

            if not events:
                break

            for event in events:
                raw_date = event.get("date", {}).get("start_date")
                start_date = None
                if raw_date:
                    for year in [start_dt.year, start_dt.year + 1]:
                        try:
                            tentative = datetime.strptime(f"{raw_date} {year}", "%b %d %Y").replace(tzinfo=timezone.utc)
                            if start_dt <= tentative <= end_dt:
                                start_date = tentative
                                break
                        except ValueError:
                            continue

                city_val = country_val = None
                address = event.get("address", [])
                if len(address) > 1:
                    city_val = address[1].split(",")[0].strip()
                    country_val = address[1].split(",")[-1].strip()

                key = f"{event.get('title')}-{event.get('link')}"
                if key in seen_keys:
                    continue
                seen_keys.add(key)

                image_urls = list(filter(None, [
                    event.get("thumbnail"),
                    event.get("image")
                ]))

                ticket_urls = [
                    t.get("link") for t in event.get("ticket_info", [])
                    if t.get("link")
                ]

                parsed_events.append(EventItem(
                    source_id=None,
                    title=event.get("title"),
                    url=event.get("link"),
                    start_date=start_date,
                    sales_start=None,
                    sales_end=None,
                    duration_seconds=None,
                    timezone="Europe/London",
                    city=city_val,
                    country=country_val,
                    venue=event.get("venue", {}).get("name"),
                    latitude=None,
                    longitude=None,
                    segment="Music",
                    genre="Pop",
                    subgenre=None,
                    category="concert",
                    labels=["concert"],
                    promoter=None,
                    attendance=None,
                    predicted_spend=None,
                    description=event.get("description"),
                    image_urls=image_urls or None,
                    ticket_urls=ticket_urls or None,
                    price=None
                ))

        await self.log(f"Received {len(parsed_events)} unique events from SerpApi")
        return parsed_events



# import logging
# from serpapi import GoogleSearch
# from typing import Any, List
# from event_model import EventItem
# from base_agent import BaseAgent
# from datetime import datetime, timezone
# from dateutil.parser import parse as parse_date


# class SerpApiAgent(BaseAgent):
#     name: str = "SerpApiAgent"

#     async def process(self, data: dict) -> List[EventItem]:
#         await self.log(f"Sending request to SerpApi for city: {data['city']}")

#         start_dt = parse_date(data["start_datetime"])
#         end_dt = parse_date(data["end_datetime"])
#         api_key = data["api_key"]
#         city = data["city"]
#         keyword = data.get("keyword", "")
#         max_pages = data.get("max_pages", 5)
#         size = data.get("size", 100)

#         query_parts = ["events"]
#         if keyword and keyword.strip().lower() != "event":
#             query_parts.append(keyword)
#         query_parts.append("in")
#         query_parts.append(city)
#         # query_parts.append(start_dt.strftime("%B %Y"))

#         base_params = {
#             "engine": "google_events",
#             "q": " ".join(query_parts),
#             "api_key": api_key,
#             "hl": "en",
#             "gl": "us"
#         }

#         parsed_events = []
#         for start_index in range(0, max_pages * size, size):
#             params = base_params.copy()
#             params["start"] = start_index
#             search = GoogleSearch(params)
#             results = search.get_dict()
#             events = results.get("events_results", [])

#             if not events:
#                 break

#             for event in events:
#                 raw_date = event.get("date", {}).get("start_date")
#                 start_date = None
#                 if raw_date:
#                     for year in [start_dt.year, start_dt.year + 1]:
#                         try:
#                             tentative = datetime.strptime(f"{raw_date} {year}", "%b %d %Y").replace(tzinfo=timezone.utc)
#                             if start_dt <= tentative <= end_dt:
#                                 start_date = tentative
#                                 break
#                         except ValueError:
#                             continue

#                 city_val = country_val = None
#                 address = event.get("address", [])
#                 if len(address) > 1:
#                     city_val = address[1].split(",")[0].strip()
#                     country_val = address[1].split(",")[-1].strip()

#                 image_urls = list(filter(None, [
#                     event.get("thumbnail"),
#                     event.get("image")
#                 ]))

#                 ticket_urls = [
#                     t.get("link") for t in event.get("ticket_info", [])
#                     if t.get("link")
#                 ]

#                 parsed_events.append(EventItem(
#                     source_id=None,
#                     title=event.get("title"),
#                     url=event.get("link"),
#                     start_date=start_date,
#                     sales_start=None,
#                     sales_end=None,
#                     duration_seconds=None,
#                     timezone="Europe/London",
#                     city=city_val,
#                     country=country_val,
#                     venue=event.get("venue", {}).get("name"),
#                     latitude=None,
#                     longitude=None,
#                     segment="Music",
#                     genre="Pop",
#                     subgenre=None,
#                     category="concert",
#                     labels=["concert"],
#                     promoter=None,
#                     attendance=None,
#                     predicted_spend=None,
#                     description=event.get("description"),
#                     image_urls=image_urls or None,
#                     ticket_urls=ticket_urls or None,
#                     price=None
#                 ))

#         await self.log(f"Received {len(parsed_events)} events from SerpApi")
#         return parsed_events




# import logging
# from serpapi import GoogleSearch
# from typing import Any, List
# from event_model import EventItem
# from base_agent import BaseAgent
# from datetime import datetime

# class SerpApiAgent(BaseAgent):
#     name: str = "SerpApiAgent"

#     async def process(self, data: dict) -> List[EventItem]:
#         await self.log(f"Sending request to SerpApi for city: {data['city']}")

#         try:
#             query_parts = ["events"]
#             if data.get("keyword"):
#                 query_parts.append(data["keyword"])
#             query_parts.append("in")
#             query_parts.append(data["city"])
#             query_parts.append(datetime.strptime(data["start_datetime"], "%Y-%m-%dT%H:%M:%SZ").strftime("%B %Y"))

#             params = {
#                 "engine": "google_events",
#                 "q": " ".join(query_parts),
#                 "api_key": data["api_key"],
#                 "hl": "en",
#                 "gl": "us"
#             }

#             search = GoogleSearch(params)
#             results = search.get_dict()
#             events = results.get("events_results", [])

#             parsed_events = []
#             for event in events:
#                 raw_date = event.get("date", {}).get("start_date")
#                 start_date = None
#                 if raw_date:
#                     try:
#                         start_date = datetime.strptime(raw_date, "%Y-%m-%d")
#                     except ValueError:
#                         try:
#                             start_date = datetime.strptime(raw_date, "%B %d, %Y")
#                         except ValueError:
#                             start_date = None

#                 item = EventItem(
#                     title=event.get("title"),
#                     url=event.get("link"),
#                     start_date=start_date,
#                     city=data["city"],
#                     venue=event.get("venue", {}).get("name"),
#                     country=None,
#                     timezone=None,
#                     genre=None,
#                     segment=None,
#                     subgenre=None,
#                     latitude=None,
#                     longitude=None,
#                     image_url=None,
#                     sales_start=None,
#                     sales_end=None,
#                     promoter=None
#                 )
#                 parsed_events.append(item)

#             await self.log(f"Received {len(parsed_events)} events from SerpApi")
#             return parsed_events

#         except Exception as e:
#             await self.handle_error(e, context=data)
#             return []
