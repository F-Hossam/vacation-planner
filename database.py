from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv
import os

load_dotenv() 

username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")

SQLA_DB_URL = f'mysql+pymysql://{username}:{password}@localhost/vacation_planner_db'

engine = create_engine(SQLA_DB_URL)

if not database_exists(engine.url):
    create_database(engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()