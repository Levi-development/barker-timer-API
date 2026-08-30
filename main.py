from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://levibarker.dev"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

solves = []

class Solve(BaseModel):
    time: float

class SolveResponse(BaseModel):
    id: int
    time: float

@app.post("/solves")
def add_solve(solve: Solve):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO solves (time) VALUES (%s)",
        (solve.time,)
    )

    connection.commit()

    cursor.close()

    return {
        "success": True,
        "solve": solve
    }


@app.get("/solves", response_model=list[SolveResponse])
def get_solves():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM solves")

    results = cursor.fetchall()

    connection.close()

    return [
        SolveResponse(id=row[0], time=row[1])
        for row in results
    ]