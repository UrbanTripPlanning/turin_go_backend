from dotenv import load_dotenv
import os

load_dotenv()

_mode = os.getenv("MODE")
dev_mode = _mode != 'prod'
# if _mode == "prod":
# SERVICE_HOST = os.getenv("PROD_HOST")
# else:
# SERVICE_HOST = os.getenv("DEV_HOST")

USER_SERVICE_URL = f'http://{os.getenv("DEV_HOST") if dev_mode else "user_service"}:{os.getenv("USER_SERVICE_PORT")}'
TRAFFIC_SERVICE_URL = f'http://{os.getenv("DEV_HOST") if dev_mode else "traffic_service"}:{os.getenv("TRAFFIC_SERVICE_PORT")}'
ROUTING_SERVICE_URL = f'http://{os.getenv("DEV_HOST") if dev_mode else "routing_service"}:{os.getenv("ROUTING_SERVICE_PORT")}'
DATA_SERVICE_URL = f'http://{os.getenv("DEV_HOST") if dev_mode else "data_service"}:{os.getenv("DATA_SERVICE_PORT")}'
REDIS_HOST = f'{os.getenv("REDIS_HOST")}' if dev_mode else "redis"
