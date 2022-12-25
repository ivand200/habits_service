import logging
from datetime import datetime
from typing import Any, Type

from fastapi import APIRouter, HTTPException, status, Depends, Body
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    APIKeyHeader,
)
import requests

from models.habits import (
    habits,
    trackers,
    HabitBase,
    UserDB,
    HabitCreate,
    HabitUpdate,
    HabitDB,
    HabitFull,
)  # type: ignore

from db import get_database  # type: ignore
from databases import Database
from settings import Settings  # type: ignore

settings: Any = Settings()
habits_router: Any = APIRouter()
api_key_header: Any = APIKeyHeader(name="Authorization")


async def get_current_user(token: str = Depends(api_key_header)) -> UserDB:
    r = requests.post(
        f"{settings.AUTH_SERVICE}/users/check-token",
        headers={"Authorization": token},
        timeout=5,
    )
    if r.status_code == 401:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_data = r.json()
    return user_data


async def get_habit_or_404(
    user_id: int, habit_id: int, database: Database = Depends(get_database)
) -> HabitBase:
    query = "SELECT id, user_id, title, description FROM habits WHERE user_id = :user_id AND id = :habit_id"
    habit_db = await database.fetch_one(
        query=query, values={"user_id": user_id, "habit_id": habit_id}
    )
    if habit_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return habit_db


@habits_router.get("/habit/{id}")
async def get_users_habit(
    id: int,
    user: dict = Depends(get_current_user),
    database: Database = Depends(get_database),
) -> HabitFull:
    """
    Get current_user habit by habit id
    """
    query = """SELECT * FROM habits WHERE user_id = :user_id AND id = :id"""
    habit_db = await database.fetch_one(
        query=query,
        values={
            "user_id": user["id"],
            "id": id,
        },
    )
    if habit_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    query = "SELECT * FROM trackers WHERE habit_id = :id"
    tracker_db = await database.fetch_all(query=query, values={"id": id})
    habit_output = HabitFull(**habit_db, tracker=tracker_db)
    return habit_output


@habits_router.post(
    "/habit", response_model=HabitDB, status_code=status.HTTP_201_CREATED
)
async def create_habit(
    habit: HabitCreate,
    user: UserDB = Depends(get_current_user),
    database: Database = Depends(get_database),
) -> HabitDB:
    """
    Create a new habit for current_user
    """
    query = """
        INSERT INTO habits(user_id, title, description)
        VALUES (:user_id, :title, :description)
        """
    new_habit = await database.execute(
        query=query,
        values={
            "user_id": user["id"],
            "title": habit.title,
            "description": habit.description,
        },
    )
    today_day = datetime.today().strftime("%d-%m-%Y")
    trackers_query = """
        INSERT INTO trackers(habit_id, date, status)
        VALUES (:habit_id, :date, :status)
        """
    await database.execute(
        query=trackers_query,
        values={
            "habit_id": new_habit,
            "date": today_day,
            "status": 0,
        },
    )
    refresh_query = "SELECT * FROM habits WHERE id = :id"
    refresh_habit = await database.fetch_one(
        query=refresh_query, values={"id": new_habit}
    )
    return refresh_habit


@habits_router.put(
    "/habit/{id}", response_model=HabitDB, status_code=status.HTTP_200_OK
)
async def update_habit(
    id: int,
    habit: HabitUpdate,
    user: UserDB = Depends(get_current_user),
    database: Database = Depends(get_database),
):
    """
    Update existing current_user habit by id
    """
    habit_db = await get_habit_or_404(user["id"], id, database)
    query = (
        "UPDATE habits SET title = :title, description = :description WHERE id = :id"
    )
    await database.execute(
        query=query,
        values={
            "title": habit.title,
            "description": habit.description,
            "id": habit_db["id"],
        },
    )
    refresh_habit = await get_habit_or_404(user["id"], id, database)
    return refresh_habit


@habits_router.put("/tracker/{tracker_id}/{status}")
async def tracker_update(
    tracker_id: int,
    status: bool,
    user: UserDB = Depends(get_current_user),
    database: Database = Depends(get_database),
):
    """
    Update tracker by id
    """
    # From trackers find habit_id
    query = "SELECT habit_id FROM trackers WHERE id = :id"
    tracker_db = await database.fetch_one(query=query, values={"id": tracker_id})

    # From habits find user_id by habit_id
    query = "SELECT user_id FROM habits WHERE id = :id"
    habit_db = await database.fetch_one(
        query=query, values={"id": tracker_db["habit_id"]}
    )

    # Check user id in response and user_id from habits
    if user["id"] != habit_db["user_id"]:
        raise HTTPException(status_code=409, detail="Wrong tracker id")

    query = "UPDATE trackers SET status = :status WHERE id = :id"
    await database.execute(query=query, values={"status": status, "id": tracker_id})

    query = "SELECT * FROM trackers WHERE id = :id"
    tracker_refresh = await database.fetch_one(query=query, values={"id": tracker_id})

    return tracker_refresh


@habits_router.delete("/habit/{id}", status_code=status.HTTP_200_OK)
async def delete_habit(
    id: int,
    user: UserDB = Depends(get_current_user),
    database: Database = Depends(get_database),
):
    """
    Delete current_user habit by id
    """
    habit_db = await get_habit_or_404(user["id"], id, database)
    query = "DELETE FROM trackers WHERE habit_id = :habit_id"
    await database.execute(query=query, values={"habit_id": habit_db[0]})
    query = "DELETE FROM habits WHERE id = :id"
    await database.execute(query=query, values={"id": habit_db[0]})
    return {"deleted": habit_db[0]}


@habits_router.get("/list")
async def get_user_habits_list(
    user: UserDB = Depends(get_current_user),
    database: Database = Depends(get_database),
):
    """
    Get current_user habits list
    """
    habits = []
    query = "SELECT * FROM habits WHERE user_id = :user_id"
    habits_db = await database.fetch_all(query=query, values={"user_id": user["id"]})
    for habit in habits_db:
        query = (
            "SELECT id, habit_id, date, status FROM trackers WHERE habit_id = :habit_id"
        )
        tracker_db = await database.fetch_all(
            query=query, values={"habit_id": habit["id"]}
        )
        habit_full = HabitFull(**habit, tracker=tracker_db)
        habits.append(habit_full)
    return habits
