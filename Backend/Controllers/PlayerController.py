from fastapi import HTTPException, Depends
from pydantic import BaseModel
from Models.team import Team  
from database import get_db
from sqlalchemy.orm import Session
