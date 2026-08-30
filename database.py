import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

connection = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="speedcube",
    user="postgres",
    password=os.environ["POSTGRES_PASSWORD"]
)