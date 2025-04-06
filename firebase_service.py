import firebase_admin
from firebase_admin import credentials, firestore
import yaml

def init_firebase(config_path: str):
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not config.get("firebase", {}).get("enabled", False):
        return None

    service_path = config["firebase"]["service_account_path"]
    cred = credentials.Certificate(service_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()
