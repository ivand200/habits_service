from typing import Any

import pytest
import requests

from settings import Settings  # type: ignore


settings: Any = Settings()


@pytest.mark.parametrize(
    "title, description, status, bool",
    [
        ("Running", "every day", 201, 1),
        ("Reading", None, 201, 1),
        (None, "no_title", 422, 0),
        ("Education", "practice", 201, 1),
    ],
)
def test_user_create_habit(user, database, title, description, status, bool) -> None:
    """
    GIVEN create a new habits by current_user, with and without title, description
    WHEN POST "/habits/habit"
    THEN check status_code == 201, habit texisting in database
    """
    payload = {"title": title, "description": description}
    r = requests.post(
        f"{settings.BACKEND}/habits/habit",
        json=payload,
        headers={"Authorization": "Bearer " + user["access_token"]},
        timeout=5,
    )
    r_body = r.json()
    cur = database.cursor()
    habit_db = cur.execute(
        "SELECT EXISTS (SELECT id, title, description FROM habits WHERE user_id = ? AND title = ?)",
        (user["id"], title),
    ).fetchone()
    tracker_db = cur.execute(
        "SELECT EXISTS(SELECT id FROM trackers WHERE habit_id = (SELECT id FROM habits WHERE user_id = ? AND title = ?))",
        (user["id"], title),
    ).fetchone()

    assert r.status_code == status
    assert habit_db[0] is bool
    assert tracker_db[0] is bool


def test_user_create_many_habits(many_habits, user, database) -> None:
    """
    GIVEN user create habits
    WHEN POST "/habits/habit
    THEN check number habits in database == created habits
    """
    for habit in range(len(many_habits)):
        r = requests.post(
            f"{settings.BACKEND}/habits/habit",
            json=many_habits[habit],
            headers={"Authorization": "Bearer " + user["access_token"]},
            timeout=5,
        )
    cur = database.cursor()
    habits_db = cur.execute(
        "SELECT id FROM habits WHERE user_id = ?", (user["id"],)
    ).fetchall()
    habits_list = [i[0] for i in habits_db]
    trackers_db = cur.execute(
        "SELECT id FROM trackers WHERE habit_id IN (?, ?, ?, ?, ?, ? ,?)",
        (tuple(habits_list)),
    ).fetchall()

    assert len(habits_db) == len(many_habits)
    assert len(trackers_db) == len(many_habits)


def test_user_get_habit_by_id(user, new_habit, database) -> None:
    """
    GIVEN get current user habit by id
    WHEN GET "habits/habit/{id}"
    THEN check status_code == 200, habit title in response, habit_id in tracker
    """
    r = requests.get(
        f"{settings.BACKEND}/habits/habit/{new_habit[0]}",
        headers={"Authorization": "Bearer " + user["access_token"]},
        timeout=5,
    )
    r_body = r.json()

    assert r.status_code == 200
    assert r_body["title"] == new_habit[1]
    assert r_body["tracker"][0]["habit_id"] == new_habit[0]


def test_user_get_habits_list(user, inserted_habits, database) -> None:
    """
    GIVEN get users habits list
    WHEN GET "/habits/list"
    THEN check status_code == 200, len list in response == list habits in database,
         resposne user_id == current_user id
    """
    r = requests.get(
        f"{settings.BACKEND}/habits/list",
        headers={"Authorization": "Bearer " + user["access_token"]},
        timeout=5,
    )
    r_body = r.json()

    assert r.status_code == 200
    assert len(r_body) == inserted_habits
    assert r_body[0]["user_id"] == user["id"]


def test_update_habit(user, new_habit, database) -> None:
    """
    GIVEN update existing user habit by id
    WHEN PUT "habits/habit/{id}"
    THEN check status_code == 200, updated title in response and in the database
    """
    payload = {"title": "updated_pytest", "description": new_habit[2]}
    r = requests.put(
        f"{settings.BACKEND}/habits/habit/{new_habit[0]}",
        json=payload,
        headers={"Authorization": "Bearer " + user["access_token"]},
        timeout=5,
    )
    r_body = r.json()
    cur = database.cursor()
    habit_db = cur.execute(
        "SELECT id, title, description FROM habits WHERE id = ?", (new_habit[0],)
    ).fetchone()

    assert r.status_code == 200
    assert habit_db[1] == r_body["title"]
    assert r_body["title"] == payload["title"]


def test_delete_habit(user, new_habit, database) -> None:
    """
    GIVEN delete users habit by id
    WHEN DELETE "habits/habits/{id}"
    THEN check status_code == 200, habit id in response, None habit in database
    """
    r = requests.delete(
        f"{settings.BACKEND}/habits/habit/{new_habit[0]}",
        headers={"Authorization": "Bearer " + user["access_token"]},
        timeout=5,
    )
    r_body = r.json()
    cur = database.cursor()
    habit_db = cur.execute(
        "SELECT id FROM habits WHERE id = ?", (new_habit[0],)
    ).fetchone()

    assert r.status_code == 200
    assert r_body["deleted"] == new_habit[0]
    assert habit_db is None
