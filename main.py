from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
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
    category: str
    scramble: str

class SolveResponse(BaseModel):
    id: int
    time: float
    timestamp: datetime
    category: str
    scramble: str

class SessionSolve(BaseModel):
    time: float
    scramble: str


class Session(BaseModel):
    category: str
    startTime: float
    sessionID: str
    youtubeVideoID: str | None
    solves: list[SessionSolve]

@app.post("/solves")
def add_solve(solve: Solve):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO solves (time, category, scramble) VALUES (%s, %s, %s)",
        (solve.time, solve.category, solve.scramble)
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
        SolveResponse(id=row[0], time=row[1], timestamp=row[2], category=row[3], scramble=row[4])
        for row in results
    ]

@app.post("/sessions")
def add_session(session: Session):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO sessions (category, start_time, youtube_video_id)
            VALUES (%s, to_timestamp(%s), %s)
            RETURNING id
            """,
            (
                session.category,
                session.startTime,
                session.youtubeVideoID
            )
        )
        session_id = cursor.fetchone()[0]

        for solve in session.solves:
            cursor.execute(
                """
                INSERT INTO solves (time, category, scramble, session_id)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    solve.time,
                    session.category,
                    solve.scramble,
                    session_id
                )
            )

        connection.commit()

        return {
            "success": True,
            "session_id": session_id,
            "solves_uploaded": len(session.solves)
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


@app.get("/sessions")
def get_sessions():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            s.id,
            s.category,
            s.start_time,
            s.youtube_video_id,
            so.id,
            so.time,
            so.timestamp,
            so.scramble
        FROM sessions s
        LEFT JOIN solves so ON so.session_id = s.id
        ORDER BY s.id DESC, so.id ASC
    """)

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    sessions = {}

    for row in results:
        session_id = row[0]

        if session_id not in sessions:
            sessions[session_id] = {
                "id": row[0],
                "category": row[1],
                "startTime": row[2],
                "youtubeVideoID": row[3],
                "solves": []
            }

        if row[4] is not None:
            sessions[session_id]["solves"].append({
                "id": row[4],
                "time": row[5],
                "timestamp": row[6],
                "scramble": row[7]
            })

    return list(sessions.values())