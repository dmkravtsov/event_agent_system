import requests
from datetime import datetime
from typing import List
from base_agent import BaseAgent
from event_model import EventItem


class PredictHQAgent(BaseAgent):
    name: str = "PredictHQAgent"
    api_key: str = ""

    async def process(self, data: dict) -> List[EventItem]:
        self.api_key = data["api_key"]
        start_datetime = data["start_datetime"]
        end_datetime = data["end_datetime"]
        origin = data.get("location_origin", "51.5074,-0.1278")
        offset_km = data.get("location_offset_km", 30)
        country = data.get("country", "GB")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

        url = "https://api.predicthq.com/v1/events/"
        size = 100
        offset = 0
        events = []

        while True:
            params = {
                "location_around.origin": origin,
                "location_around.offset": f"{offset_km}km",
                "country": country,
                "scope": "locality",  # остаётся в коде
                "start.gte": start_datetime,
                "start.lte": end_datetime,
                "limit": size,
                "offset": offset,
                "sort": "start"
            }

            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data_json = response.json()
                results = data_json.get("results", [])
                if not results:
                    break

                for e in results:
                    geo = e.get("geo", {})
                    addr = geo.get("address", {})
                    events.append(EventItem(
                        source_id=e.get("id"),
                        title=e.get("title"),
                        url=None,
                        start_date=e.get("start"),
                        sales_start=None,
                        sales_end=None,
                        duration_seconds=e.get("duration"),
                        timezone=e.get("timezone"),
                        city=addr.get("locality"),
                        country="United Kingdom",
                        venue=(e.get("entities", [{}])[0].get("name") if e.get("entities") else None),
                        latitude=e.get("location", [None, None])[1],
                        longitude=e.get("location", [None, None])[0],
                        segment=None,
                        genre=None,
                        subgenre=None,
                        category=e.get("category"),
                        labels=e.get("labels"),
                        promoter=None,
                        attendance=e.get("phq_attendance"),
                        predicted_spend=e.get("predicted_event_spend"),
                        description=e.get("description"),
                        image_urls=None,
                        ticket_urls=None,
                        price=None
                    ))

                offset += size
                if not data_json.get("overflow"):
                    break

            except Exception as e:
                await self.handle_error(e, context=data)
                break

        await self.log(f"PredictHQAgent parsed {len(events)} events")
        return events


# import requests
# from datetime import datetime
# from typing import List
# from base_agent import BaseAgent
# from event_model import EventItem


# class PredictHQAgent(BaseAgent):
#     name: str = "PredictHQAgent"
#     api_key: str = ""

#     async def process(self, data: dict) -> List[EventItem]:
#         self.api_key = data["api_key"]
#         city = data["city"]
#         start_datetime = data["start_datetime"]
#         end_datetime = data["end_datetime"]
#         size = data.get("size", 100)
#         max_pages = data.get("max_pages", 100)  # добавлено для гибкости

#         headers = {
#             "Authorization": f"Bearer {self.api_key}",
#             "Accept": "application/json"
#         }

#         url = "https://api.predicthq.com/v1/events/"
#         offset = 0
#         page = 0
#         events = []

#         while page < max_pages:
#             params = {
#                 "location_around.origin": "51.5074,-0.1278",  # фиксировано для Лондона
#                 "location_around.offset": "30km",
#                 "country": "GB",
#                 "scope": "locality",
#                 "start.gte": start_datetime,
#                 "start.lte": end_datetime,
#                 "limit": size,
#                 "offset": offset,
#                 "sort": "start"
#             }

#             try:
#                 response = requests.get(url, headers=headers, params=params)
#                 response.raise_for_status()
#                 data = response.json()
#                 results = data.get("results", [])
#                 if not results:
#                     break

#                 for e in results:
#                     geo = e.get("geo", {})
#                     addr = geo.get("address", {})
#                     item = EventItem(
#                         source_id=e.get("id"),
#                         title=e.get("title"),
#                         url=None,
#                         start_date=e.get("start"),
#                         sales_start=None,
#                         sales_end=None,
#                         duration_seconds=e.get("duration"),
#                         timezone=e.get("timezone"),
#                         city=addr.get("locality"),
#                         country="United Kingdom",
#                         venue=(e.get("entities", [{}])[0].get("name") if e.get("entities") else None),
#                         latitude=e.get("location", [None, None])[1],
#                         longitude=e.get("location", [None, None])[0],
#                         segment=None,
#                         genre=None,
#                         subgenre=None,
#                         category=e.get("category"),
#                         labels=e.get("labels"),
#                         promoter=None,
#                         attendance=e.get("phq_attendance"),
#                         predicted_spend=e.get("predicted_event_spend"),
#                         description=e.get("description"),
#                         image_urls=None,
#                         ticket_urls=None,
#                         price=None
#                     )
#                     events.append(item)

#                 offset += size
#                 page += 1
#                 if not data.get("overflow"):
#                     break

#             except Exception as e:
#                 await self.handle_error(e, context=data)
#                 break

#         await self.log(f"PredictHQAgent parsed {len(events)} events")
#         return events
