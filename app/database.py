# make this file second to create and connect to the database

from contextlib import contextmanager # janitor for cleaning up random database session junk
from sqlmodel import Session, SQLModel, create_engine # 1-> allows the database to be created, 2-> allows us tables (classes) to be created, 3-> allows us to run queries
from typing import Annotated # type hinting for fastapi endpoints
from fastapi import Depends # handles some ugly dependency injection for us
from . import models # connects the tables (classes) we created in models.py to the database

sqlite_file_name = "database.db" # literally just naming the soon to be file
sqlite_url = f"sqlite:///{sqlite_file_name}" # actually making and finding the database file

# some fancy boilerplate to connect to the database and make sure it works with multiple threads (like when we run the server and cli at the same time)
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

# boilerplate tier code finally, we make the database and tables into something real with this function
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# boilerplate tier code, mass delete, for testing purposes
def drop_all():
    SQLModel.metadata.drop_all(bind=engine)
    
# boilerplate tier code, we create a session to do things in it, automatically closes the session when we're done, so we don't have to worry about it
@contextmanager
def get_session():
    with Session(engine) as session:
        yield session

# connects api endpoints to the database session, so we can do things in the database from the endpoints
SessionDep = Annotated[Session, Depends(get_session)]