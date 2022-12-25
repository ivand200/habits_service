import sqlalchemy
from databases import Database
from settings import Settings


settings = Settings()


DATABASE_URL = str(settings.database_habits)
database = Database(DATABASE_URL)
sqlalchemy_engine = sqlalchemy.create_engine(DATABASE_URL)

metadata = sqlalchemy.MetaData()

# Dependency
def get_database() -> Database:
    return database