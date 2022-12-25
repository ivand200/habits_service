from fastapi import FastAPI
import uvicorn

from db import get_database, metadata, sqlalchemy_engine
from routers.habits import habits_router

app = FastAPI()


@app.on_event("startup")
async def startup():
    await get_database().connect()
    metadata.create_all(sqlalchemy_engine)


@app.on_event("shutdown")
async def shutdown():
    await get_database().disconnect()


app.include_router(habits_router, prefix="/habits", tags=["habits"])


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8888)

