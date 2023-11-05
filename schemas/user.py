from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str


class UserInDB(UserBase):
    password: str

    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(UserBase):
    pass

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str
    password: str
