import yaml
import os
import requests
import json
from datetime import datetime
import dateparser

today = datetime.utcnow().strftime("%Y-%m-%dT00:00:00Z")

# Загрузка конфигурации
with open(os.path.join(os.path.dirname(__file__), "../config.yaml"), "r") as f:
    config = yaml.safe_load(f)

api_key = config["openrouter"]["api_key"]
model = config["openrouter"]["model"]

# Системный промпт
system_prompt = (
    f"You are a smart and cheerful assistant helping the user find events.\n"
    f"Today is {today}.\n"
    "Start with a warm short greeting and immediately ask what type of event, city and when — all in one sentence.\n"
    "Do NOT ask for ISO date format. The user can speak freely, and you should interpret it intelligently.\n"
    "Don't make up anything on your own.\n"
    "Do not mention JSON or give examples.\n"
    "Always assume the year is 2025 if not specified.\n"
    "When all required data is collected (event type, city, date range), output only valid JSON in triple quotes:\n"
    "\"\"\"\n{\"city\": \"London\", \"keyword\": \"concert\", \"start_datetime\": \"2025-04-10T00:00:00Z\", \"end_datetime\": \"2025-04-20T00:00:00Z\"}\n\"\"\"\n"
    "Before that — guide the user conversationally."
)

# Инициализация истории
messages = [
    {
        "role": "system",
        "content": [{"type": "text", "text": system_prompt}]
    }
]

def call_openrouter(messages):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": model,
        "messages": messages
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"]  # ✅ content — это строка
    except Exception as e:
        print("❌ Error from OpenRouter response:")
        print(json.dumps(response.json(), indent=2))
        raise e


def normalize_dates_in_json(json_str):
    try:
        data = json.loads(json_str)
        start = dateparser.parse(data["start_datetime"], settings={"RELATIVE_BASE": datetime(2025, 1, 1)})
        end = dateparser.parse(data["end_datetime"], settings={"RELATIVE_BASE": datetime(2025, 1, 1)})
        data["start_datetime"] = start.strftime("%Y-%m-%dT00:00:00Z")
        data["end_datetime"] = end.strftime("%Y-%m-%dT00:00:00Z")
        return data
    except Exception:
        return None

# Первый вопрос от модели
reply = call_openrouter(messages)
print(f"Assistant: {reply}")
messages.append({"role": "assistant", "content": [{"type": "text", "text": reply}]})

# Диалог
while True:
    user_input = input("You: ")
    messages.append({"role": "user", "content": [{"type": "text", "text": user_input}]})

    reply = call_openrouter(messages)
    print(f"Assistant: {reply}")
    messages.append({"role": "assistant", "content": [{"type": "text", "text": reply}]})

    # Проверка на JSON в тройных кавычках
    if '```' in reply or '"""' in reply:
        json_start = reply.find('{')
        json_end = reply.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            json_str = reply[json_start:json_end]
            parsed = normalize_dates_in_json(json_str)
            if parsed:
                print("\n✅ Data collected for next agents:")
                print(json.dumps(parsed, indent=2))
                break



#######mistral#############
# import yaml
# import os
# import requests
# import json
# from datetime import datetime, timedelta
# import dateparser

# today = datetime.utcnow().strftime("%Y-%m-%dT00:00:00Z")

# # Загрузка конфигурации
# with open(os.path.join(os.path.dirname(__file__), "../config.yaml"), "r") as f:
#     config = yaml.safe_load(f)

# api_key = config["openrouter"]["api_key"]
# model = config["openrouter"]["model"]

# # Системный промт
# messages = [
#     {
#         "role": "system",
#         "content": (
#             f"You are a smart and cheerful assistant helping the user find events.\n"
#             f"Today is {today}.\n"
#             "Start with a warm short greeting and immediately ask what type of event, city and when in one sentence and without samples.\n"
#             "Do NOT ask for ISO date format. The user can speak freely, and you should interpret it intelligently.\n"
#             "Don't make up anything on your own.\n"
#             "Once you have all the information, return only JSON like this in triple quotes:\n"
#             "{\"city\": \"London\", \"keyword\": \"concert\", \"start_datetime\": \"2025-04-10T00:00:00Z\", \"end_datetime\": \"2025-04-20T00:00:00Z\"}\n"
#             "Until then, just talk casually and guide the user."
#         )
#     }
# ]

# def call_openrouter(messages):
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type": "application/json"
#     }
#     body = {
#         "model": model,
#         "messages": messages
#     }
#     response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
#     return response.json()["choices"][0]["message"]["content"]

# def normalize_dates_in_json(json_str):
#     try:
#         data = json.loads(json_str)
#         start = dateparser.parse(data["start_datetime"], settings={"PREFER_DATES_FROM": "future", "RELATIVE_BASE": datetime(2025, 1, 1)})
#         end = dateparser.parse(data["end_datetime"], settings={"PREFER_DATES_FROM": "future", "RELATIVE_BASE": datetime(2025, 1, 1)})
#         data["start_datetime"] = start.strftime("%Y-%m-%dT00:00:00Z")
#         data["end_datetime"] = end.strftime("%Y-%m-%dT00:00:00Z")
#         return data
#     except:
#         return None

# # Первый вопрос от модели
# reply = call_openrouter(messages)
# print(f"Assistant: {reply}")
# messages.append({"role": "assistant", "content": reply})

# # Диалог
# while True:
#     user_input = input("You: ")
#     messages.append({"role": "user", "content": user_input})

#     reply = call_openrouter(messages)
#     print(f"Assistant: {reply}")
#     messages.append({"role": "assistant", "content": reply})

#     if reply.strip().startswith("{") and reply.strip().endswith("}"):
#         parsed = normalize_dates_in_json(reply)
#         if parsed:
#             print("\n✅ Data collected for next agents:")
#             print(json.dumps(parsed, indent=2))
#             break
