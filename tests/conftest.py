import sqlite3
import random
from typing import Any
from datetime import datetime, timedelta

import pytest
import requests

from settings import Settings  # type: ignore


settings: Any = Settings()


# {
#     "email": "pytest@ppp.com",
#     "username": "pytest",
#     "password": "password"
# }


@pytest.fixture(scope="function")
def database():
    con = sqlite3.connect("habits.db")
    cur = con.cursor()
    # cur.execute("DELETE FROM trackers")
    # cur.execute("DELETE FROM habits")
    # con.commit()
    yield con
    cur.execute("DELETE FROM trackers")
    cur.execute("DELETE FROM habits")
    con.commit()
    con.close()


@pytest.fixture(scope="function")
def user(database):
    data = {"email": "pytest@ppp.com", "password": "password"}
    r_login = requests.post(
        f"{settings.AUTH_SERVICE}/users/login",
        json=data,
        timeout=5,
    )
    r_login_body = r_login.json()
    r = requests.post(
        f"{settings.AUTH_SERVICE}/users/check-token",
        headers={"Authorization": "Bearer " + r_login_body["access_token"]},
        timeout=5,
    )
    r_body = r.json()
    return r_body


@pytest.fixture(scope="function")
def many_habits(database):
    count = 7
    habits = []
    for i in range(count):
        payload = {"title": f"test_{i}", "description": f"desc_{i+1}"}
        habits.append(payload)
    return habits


@pytest.fixture(scope="function")
def new_habit(database, user):
    data = {
        "title": "pytest",
        "description": "The one habit",
    }
    cur = database.cursor()
    cur.execute(
        "INSERT INTO habits(user_id, title, description) VALUES (?, ?, ?) ",
        (user["id"], data["title"], data["description"]),
    )
    habit_db = cur.execute(
        "SELECT id, title, description FROM habits WHERE title = ?", (data["title"],)
    ).fetchone()
    today_day = datetime.today().strftime("%d-%m-%Y")
    cur.execute(
        "INSERT INTO trackers(habit_id, date, status) VALUES (?, ?, ?)",
        (habit_db[0], today_day, 0),
    )
    database.commit()
    yield habit_db


@pytest.fixture(scope="function")
def inserted_habits(database, user):
    count = 6
    habits = []
    # today_day = datetime.today().strftime("%d-%m-%Y")
    today_day = datetime.today()
    cur = database.cursor()
    for i in range(count):
        title = f"test_{i}_pytest"
        description = f"test_desc_{i}"
        date = today_day + timedelta(days=1)
        cur.execute(
            "INSERT INTO habits (user_id, title, description) VALUES (?, ?, ?) ",
            (user["id"], title, description),
        )
        habit_db = cur.execute(
            "SELECT id FROM habits WHERE title = (?)", (title,)
        ).fetchone()
        cur.execute(
            "INSERT INTO trackers (habit_id, date, status) VALUES (?, ?, ?)",
            (habit_db[0], date.strftime("%d-%m-%Y"), 0),
        )
        database.commit()
    return count
