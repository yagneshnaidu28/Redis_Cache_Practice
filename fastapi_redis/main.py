from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from pydantic import BaseModel
import redis
import json

from database import Base, engine, SessionLocal

app = FastAPI()

# MySQL table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100))


Base.metadata.create_all(bind=engine)


# Redis connection
r = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)


# Database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Request schema
class UserSchema(BaseModel):
    name: str
    email: str


# CREATE USER
@app.post("/users")
def create_user(user: UserSchema, db: Session = Depends(get_db)):

    new_user = User(name=user.name, email=user.email)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    r.delete("users:all")

    return {"message": "User created", "id": new_user.id}


# GET ALL USERS
@app.get("/users")
def get_users(db: Session = Depends(get_db)):

    cached_users = r.get("users:all")

    if cached_users:
        return json.loads(cached_users)

    users = db.query(User).all()

    result = [
        {"id": u.id, "name": u.name, "email": u.email}
        for u in users
    ]

    r.set("users:all", json.dumps(result), ex=300)

    return result


# GET SINGLE USER
@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):

    cache_key = f"user:{user_id}"

    cached_user = r.get(cache_key)

    if cached_user:
        return json.loads(cached_user)

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }

    r.set(cache_key, json.dumps(result), ex=300)

    return result


# UPDATE USER
@app.put("/users/{user_id}")
def update_user(
    user_id: int,
    data: UserSchema,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = data.name
    user.email = data.email

    db.commit()

    r.delete(f"user:{user_id}", "users:all")

    return {"message": "User updated"}


# DELETE USER
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    r.delete(f"user:{user_id}", "users:all")

    return {"message": "User deleted"}