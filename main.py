from fastapi import FastAPI
from pydantic import BaseModel

from database import get_connection

app = FastAPI()

solves = []

class Solve(BaseModel):
    time: float


@app.post("/solves")
def add_solve(solve: Solve):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(f"INSERT INTO solves (time) VALUES ({solve.time})")

    connection.commit()

    cursor.close()

    return {
        "success": True,
        "solve": solve
    }


@app.get("/solves")
def get_solves():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM solves")

    results = cursor.fetchall()

    cursor.close()

    return results