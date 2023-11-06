from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str


class UserInDB(UserBase):
    password_hash: str

    model_config = ConfigDict(from_attributes=True)


class User(UserBase):

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(UserBase):
    pass

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str
    password: str
