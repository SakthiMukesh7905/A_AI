import os
from pathlib import Path
from dotenv import load_dotenv

# Find project root directory
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "SignAlert Real-Time ISL Emergency Dispatcher"
    BASE_DIR: Path = BASE_DIR
    MODEL_PATH: str = os.getenv("MODEL_PATH", str(BASE_DIR / "sign_model.h5"))
    LABEL_MAP_PATH: str = os.getenv("LABEL_MAP_PATH", str(BASE_DIR / "label_map.json"))
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_NUMBER: str = os.getenv("TWILIO_FROM_NUMBER", "")
    CAREGIVER_PHONE_NUMBER: str = os.getenv("CAREGIVER_PHONE_NUMBER", "+1234567890")
    SECONDARY_CAREGIVER_PHONE_NUMBER: str = os.getenv("SECONDARY_CAREGIVER_PHONE_NUMBER", "")
    CALL_TIMEOUT_SECONDS: int = int(os.getenv("CALL_TIMEOUT_SECONDS", "15"))
    
    # Emergency & Cooldown Rules
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.70"))
    COOLDOWN_SECONDS: int = int(os.getenv("COOLDOWN_SECONDS", "30"))
    
    # Buffer & Sequence Length
    SEQUENCE_LENGTH: int = 30
    
    # Allow voice call in addition to SMS
    ENABLE_VOICE_CALL: bool = os.getenv("ENABLE_VOICE_CALL", "true").lower() in ("1", "true", "yes")

settings = Settings()
