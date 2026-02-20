# make this file first to define the tables

from sqlmodel import Field, SQLModel # 1-> defines the columns, 2-> allows us to make tables (classes) 
from typing import Optional # database handles the primary key for optional makes it so we can define the id in the class but then forgot about it
from pwdlib import PasswordHash # password hashing

password_hash = PasswordHash.recommended()

class User(SQLModel, table=True):
    id: Optional[int] =  Field(default=None, primary_key=True)
    username:str = Field(index=True, unique=True)
    email:str = Field(index=True, unique=True)
    password:str
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
        
    def set_password(self, password):
        self.password = password_hash.hash(password)
        
    def __str__(self) -> str:
        return f"(User id={self.id}, username={self.username}, email={self.email})"