import os
from dotenv import load_dotenv

load_dotenv()

TOOL_REGISTRY_URL = os.getenv("TOOL_REGISTRY_URL", "http://tool_registry:8003")
