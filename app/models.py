# make this file first to define the tables

from sqlmodel import Field, SQLModel, Relationship # 1-> defines the columns, 2-> allows us to make tables (classes), 3-> allows us to define relationships between classes/tables 
from typing import Optional # database handles the primary key for optional makes it so we can define the id in the class but then forgot about it
from pwdlib import PasswordHash # password hashing

password_hash = PasswordHash.recommended()

class User(SQLModel, table=True):
    id: Optional[int] =  Field(default=None, primary_key=True)
    username:str = Field(index=True, unique=True)
    email:str = Field(index=True, unique=True)
    password:str
    
    # capital T so refers to the python class since we're defining the relationship between the two tables, 
    # not defining the column in the database. if we were defining the column in the database, 
    # then we would use lowercase t and refer to the table name, as seen in Todo class where 
    # we refer to the user table with lowercase u
    todos: list['Todo'] = Relationship(back_populates="user") # relationship between the two tables, back_populates is used to define the relationship in the other table
    # datatype of Todo, list['...'] is notify that it's a list
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
        
    def set_password(self, password):
        self.password = password_hash.hash(password)
        
    def __str__(self) -> str:
        return f"(User id={self.id}, username={self.username}, email={self.email})"
 
class TodoCategory(SQLModel, table=True):
    todo_id: int|None = Field(primary_key=True, foreign_key='todo.id')
    category_id: int|None = Field(primary_key=True, foreign_key='category.id')   

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id") # common u so refers to table name and then column name
    text: str = Field(max_length=255)
    done: bool = Field(default=False)
    
    # column_name: datatype (can also be a class, hence capital U, for relationships) = Relationship(back_populates="column_name") column name so hence lowercase
    user: User = Relationship(back_populates="todos") # relationship between the two tables, back_populates is used to define the relationship in the other table   
    categories: list['Category'] = Relationship(back_populates=("todos"), link_model=TodoCategory)
    
    def toggle(self):
        self.done = not self.done
    
class Category(SQLModel, table=True):
    id: Optional[int] =  Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key='user.id') #set user_id as a foreign key to user.id 
    text: str = Field(max_length=255)

    todos: list['Todo'] = Relationship(back_populates=("categories"), link_model=TodoCategory)