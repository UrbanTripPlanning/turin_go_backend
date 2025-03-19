from dotenv import load_dotenv
import os

load_dotenv()

_mode = os.getenv("MODE")
if _mode == "prod":
    SERVICE_HOST = os.getenv("PROD_HOST")
else:
    SERVICE_HOST = os.getenv("DEV_HOST")

USER_SERVICE_URL = f'{SERVICE_HOST}:{os.getenv("USER_SERVICE_PORT")}'
TRAFFIC_SERVICE_URL = f'{SERVICE_HOST}:{os.getenv("TRAFFIC_SERVICE_PORT")}'
ROUTING_SERVICE_URL = f'{SERVICE_HOST}:{os.getenv("ROUTING_SERVICE_PORT")}'
DATA_SERVICE_URL = f'{SERVICE_HOST}:{os.getenv("DATA_SERVICE_PORT")}'
