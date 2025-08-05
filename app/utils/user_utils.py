

from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.user.user import User


def check_unique_username_email(session: Session, username: str = None, email: str = None, exclude_user_id: int = None):
    if email:
        query = select(User).where(User.email == email)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        if session.exec(query).first():
            raise HTTPException(status_code=409, detail="Email já está em uso por outro usuário.")

    if username:
        query = select(User).where(User.username == username)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        if session.exec(query).first():
            raise HTTPException(status_code=409, detail="Username já está em uso por outro usuário.")