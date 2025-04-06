import asyncio
import json
import os
from datetime import datetime, timedelta
from agents.agent_ticketmaster import TicketmasterAgent
from agents.agent_serpapi import SerpApiAgent
from config_loader import load_config
from event_model import EventItem
from firebase_admin import credentials, firestore, initialize_app
import re


def interpret_user_input(user_input: str, default_city: str) -> dict:
    now = datetime.utcnow()
    user_input = user_input.lower()

    keyword_match = re.search(r"(concert|music|show|exhibition|festival|event|sports|play|musical|opera)", user_input)
    keyword = keyword_match.group(1) if keyword_match else None

    classification_map = {
        "concert": "music",
        "music": "music",
        "show": "arts & theatre",
        "exhibition": "arts & theatre",
        "festival": "music",
        "sports": "sports",
        "play": "arts & theatre",
        "musical": "arts & theatre",
        "opera": "arts & theatre"
    }
    classification = classification_map.get(keyword)

    if "weekend" in user_input:
        weekday = now.weekday()
        days_to_saturday = (5 - weekday) % 7
        start = now + timedelta(days=days_to_saturday)
        end = start + timedelta(days=2)
    elif "two weeks" in user_input or "2 weeks" in user_input:
        start = now
        end = now + timedelta(days=14)
    elif "month" in user_input:
        start = now
        end = now + timedelta(days=30)
    elif "three months" in user_input or "3 months" in user_input:
        start = now
        end = now + timedelta(days=90)
    else:
        start = now
        end = now + timedelta(days=30)

    known_cities = ["miami", "dubai", "london", "milan"]
    city = next((c.title() for c in known_cities if c in user_input), default_city)

    return {
        "city": city,
        "start_datetime": start.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "end_datetime": end.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "keyword": keyword,
        "classificationName": classification
    }


async def main():
    config = load_config()
    user_input = input("What kind of event are you looking for? ")

    # Initialize Firebase
    cred_path = config["firebase"]["service_account"]
    cred = credentials.Certificate(cred_path)
    initialize_app(cred)
    db = firestore.client()

    query_data_tm = interpret_user_input(user_input, config["ticketmaster"]["default_city"])
    query_data_tm["api_key"] = config["ticketmaster"]["api_key"]
    query_data_tm["size"] = config["ticketmaster"].get("default_size", 10)

    query_data_serp = interpret_user_input(user_input, config["serpapi"]["default_city"])
    query_data_serp["api_key"] = config["serpapi"]["api_key"]
    query_data_serp["size"] = config["serpapi"].get("default_size", 10)

    agents = []
    if config["ticketmaster"].get("enabled", True):
        agents.append(TicketmasterAgent().process(query_data_tm))
    if config["serpapi"].get("enabled", True):
        agents.append(SerpApiAgent().process(query_data_serp))

    all_results: list[EventItem] = []
    for result_set in await asyncio.gather(*agents):
        all_results.extend(result_set)

    os.makedirs("logs", exist_ok=True)
    unique_events = {}
    for event in all_results:
        key = f"{(event.title or '').strip().lower()}|{(event.venue or '').strip().lower()}|{event.start_date}"
        if key not in unique_events:
            unique_events[key] = event
        else:
            with open("logs/duplicates.log", "a", encoding="utf-8") as dup_log:
                dup_log.write(json.dumps(event.model_dump(), ensure_ascii=False, default=str) + "\n")

    deduplicated_results = list(unique_events.values())

    print("\n🎯 Found events:\n")
    output = []
    for event in deduplicated_results:
        print(f"- {event.title} | {event.start_date} | {event.city} | {event.url}")
        doc = db.collection("events").document()
        doc.set(event.model_dump(mode="json"))
        output.append(event.model_dump())

    with open("logs/events.log", "a", encoding="utf-8") as log_file:
        for entry in output:
            log_file.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")

    with open("results.json", "w", encoding="utf-8") as result_file:
        json.dump(output, result_file, ensure_ascii=False, indent=2, default=str)


if __name__ == "__main__":
    asyncio.run(main())
