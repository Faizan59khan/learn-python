# fastapi_neon/settings.py

from starlette.config import Config

from starlette.datastructures import Secret



try:

   config = Config(".env")

except FileNotFoundError:

   config = Config()



DATABASE_URL = config("DATABASE_URL", cast=Secret)   

# Here are credential's are loading from env