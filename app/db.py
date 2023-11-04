from databases import Database
from os import environ

database = Database(environ.get("DB_CONNECTION_STRING", "mysql+asyncmy://nure_db_cw:123456789@127.0.0.1/nure_db_cw"))
