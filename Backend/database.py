from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from fastapi import Depends
from typing import Annotated
import os

# just loads .env files
load_dotenv()

#gets .env variables for the database connection
dbUser = os.getenv('DB_USER')
dbPassword = os.getenv('DB_PASSWORD')
dbHost = os.getenv('DB_HOST')
dbPort = os.getenv('DB_PORT')
dbName = os.getenv('DB_NAME')

# creates the database URL for SQLAlchemy
URL_DATABASE = f'postgresql://{dbUser}:{dbPassword}@{dbHost}:{dbPort}/{dbName}'

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Database dependency to get a session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dbDependancy = Annotated[SessionLocal, Depends(get_db)]




