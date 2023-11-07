import os
from bytepit_api.database.database import Database

db = Database(os.environ["DB_CONNECTION_STRING"])
