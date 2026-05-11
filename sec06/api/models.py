from datetime import datetime

from sqlmodel import Field, SQLModel


class UserModel(SQLModel, table=True):
	username: str = Field(primary_key=True)
	hashed_password: str


class MessageModel(SQLModel, table=True):
	id: int | None = Field(default=None, primary_key=True)
	name: str
	message: str | None = None
	important: bool = False
	time: datetime
	update_time: datetime
