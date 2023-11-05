from datetime import timedelta, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine
from schemas.user import User, UserInDB, UserUpdate

models.Base.metadata.create_all(bind=engine)

router = APIRouter()


SECRET_KEY = "016a5ba1b6ead05abc518c5676421b3ab3346e09191385bd41284bc1366369a9"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    # if user is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrectt credential")
    #
    return user


def authenticate_user(username: str, password: str, db: Session):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/register", response_model=User)
async def register_user(user: UserInDB, db: Session = Depends(get_db)):
    # check if username has been taken
    user_get = db.query(models.User).filter(
        models.User.username == user.username or models.User.email == user.email
    ).first()
    if user_get is not None:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="username or email has been taken")

    # save user details to database
    new_user = models.User(
        username=user.username,
        password_hash=get_password_hash(user.password),  # hash the password
        email=user.email,
        full_name=user.full_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# @router.post("/login")
# async def login_user(user: UserLogin, user_repo: Session = Depends(get_db)):
#     get_user = user_repo.query(models.User).filter(models.User.username == user.username).first()
#     if get_user is None or not verify_password(user.password, get_user.password):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect username or password")

#     expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     expires_delta = datetime.utcnow() + expires

#     to_encode = {"sub": user.username, "exp": expires_delta}
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#     return {"access_token": encoded_jwt, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = authenticate_user(db=db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile", response_model=User)
async def get_user_profile(current_user: Annotated[User, Depends(get_current_active_user)]):

    return current_user


@router.put("/profile", response_model=User)
async def update_user_profile(
        updated_user: UserUpdate,
        current_user: Annotated[User, Depends(get_current_active_user)],
        db=Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    for key, value in updated_user.model_dump().items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user
