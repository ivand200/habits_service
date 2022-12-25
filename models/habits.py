import time

from datetime import datetime, timedelta
from typing import List, Union, Optional
from pydantic import BaseModel, Field, EmailStr
import sqlalchemy
from db import metadata


class UserBase(BaseModel):
    email: EmailStr
    username: str

    class Config:
        orm_mode = True


class UserDB(UserBase):
    id: int

    class Config:
        orm_mode = True


class HabitCreate(BaseModel):
    title: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class HabitBase(HabitCreate):
    user_id: int

    class Config:
        orm_mode = True


class HabitDB(HabitBase):
    id: int

    class Config:
        orm_mode = True


class HabitUpdate(BaseModel):
    title: str
    description: str

    class Config:
        orm_mode = True

class TrackerBase(BaseModel):
    habit_id: int
    date: str
    status: int

    class Config:
        orm_mode = True


class HabitFull(HabitDB):
    tracker: Optional[List[TrackerBase]]


habits = sqlalchemy.Table(
    "habits",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("description", sqlalchemy.String),
)


trackers = sqlalchemy.Table(
    "trackers",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("habit_id", sqlalchemy.ForeignKey("habits.id"), nullable=False),
    sqlalchemy.Column("date", sqlalchemy.Date(), nullable=False),
    sqlalchemy.Column("status", sqlalchemy.Integer, default=False),
)
