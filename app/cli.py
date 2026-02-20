# make this file last since this is where you actually use the database and tables

from typing_extensions import Annotated # allows for defualt arguments in CLI commands (like limit and offset in get_paginated)

# cli uses absolute addressing since it's a CLI and not a module, so we need to import from the app package instead of the current directory
import typer # allows us to make CLI commands
from app.database import create_db_and_tables, get_session, drop_all # carry over the database functions we made in database.py
from app.models import User # carry over the User table we made in models.py
from fastapi import Depends # handles some ugly dependency injection for us
from sqlmodel import select # allows us to run select queries on the database
from sqlalchemy.exc import IntegrityError # allows us to catch database errors (like when we try to create a user with a username that already exists)

cli = typer.Typer()

# how to use help= when there's no arguments, since the help text can't be attached to an argument in this case
@cli.command(help="Initializes the database by creating tables and adding a default user (bob)")
def initialize():
    '''
    Creates the database and tables, and adds a default user (bob) to the database. 
    
    Args:
        None
    
    Usage:
        python -m app.cli initialize
    '''
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User('bob', 'bob@mail.com', 'bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")

@cli.command()
def get_user(username: Annotated[str, typer.Argument(help="The username of the user to retrieve")]):
    '''
    Retrieve a user from the database by username.

    Args:
        username: The username of the user to retrieve.

    Usage:
        python -m app.cli get-user <username>
    '''
    with get_session() as db:  # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first() # Run a query to find the user with the given username
        if not user:
            print(f'{username} not found!')
            return
        print(user)

@cli.command(help="Retrieves all users from the database and prints their information")
def get_all_users():
    '''
    Retrieves all users from the database and prints their information.
    
    Args:
        None
        
    Usage:
        python -m app.cli get-all-users
    '''
    with get_session() as db: # Get a connection to the database
        all_users = db.exec(select(User)).all() # Run a query to get all users
        if not all_users:
            print("No users found")
            return
        else:
            for user in all_users:
                print(user)

@cli.command()
def change_email(username: Annotated[str, typer.Argument(help="The username of the user whose email is to be changed")], 
                 new_email: Annotated[str, typer.Argument(help="The new email address for the user")]):
    '''
    Modifies the email address of a user in the database.
    
    Args:
        username: The username of the user whose email is to be changed.
        new_email: The new email address for the user.
    
    Usage:
        python -m app.cli change-email <username> <new_email>
    '''
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first() # Run a query to find the user with the given username
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email # Update the user's email
        db.add(user) # Tell the database about this change
        db.commit() # Tell the database to persist this change
        print(f"Updated {user.username}'s email to {user.email}")

@cli.command()
def create_user(username: Annotated[str, typer.Argument(help="The username of the new user")], 
                email: Annotated[str, typer.Argument(help="The email address of the new user")], 
                password: Annotated[str, typer.Argument(help="The password for the new user")]):
    '''
    Creates a new user in the database with the provided username, email, and password.
    
    Args:
        username: The username of the new user.
        email: The email address of the new user.
        password: The password for the new user.
        
    Usage:
        python -m app.cli create-user <username> <email> <password>
    '''
    with get_session() as db:
        new_user = User(username, email, password) 
        try:
            db.add(new_user)
            db.commit()
        except IntegrityError as e:
            db.rollback() # If there was an error, we need to rollback the transaction so we can try again
            print(f"Error: A user with the username '{username}' already exists.")
            return
        else:
            print(new_user)
            
@cli.command()
def delete_user(username: Annotated[str, typer.Argument(help="The username of the user to delete")]):
    '''
    Deletes a user from the database with the given username.
    
    Args:
        username: The username of the user to delete.
        
    Usage:
        python -m app.cli delete-user <username>
    '''
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first() # Run a query to find the user with the given username
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f"Deleted user {username}")

@cli.command()
def get_partial_user(partial_username: Annotated[str, typer.Argument(help="The partial username to search for")], 
                    partial_email: Annotated[str, typer.Argument(help="The partial email to search for")]):
    '''
    Gets a user from the database with a partially specified username or email.
    
    Args:
        partial_username: The partial username to search for.
        partial_email: The partial email to search for.
        
    Usage:
        python -m app.cli get-partial-user <partial_username> <partial_email>
    '''
    with get_session() as db:
        user = db.exec(select(User).where(User.username.contains(partial_username) | User.email.contains(partial_email))).first() # where is just like the WHERE clause in SQL, so it can take an OR statement in the form of |, and the contains method can be used to search for partial matches in the username and email columns
        if not user:
            print(f'No user found with username containing "{partial_username}" or email containing "{partial_email}"')
            return
        print(user)
        
        
# how to specifically set default arguments in CLI commands, it's a different method from regular python function defaults
@cli.command()
def get_paginated(limit: Annotated[int, typer.Argument(help="The number of maximum number of users to return")] = 10, 
                  offset: Annotated[int, typer.Argument(help="The number of users to skip before starting to return results")] = 0):
    '''
    Gets a paginated list of users from the database.
    
    Args:
        limit: The maximum number of users to return (default is 10).
        offset: The number of users to skip before starting to return results (default is 0).
        
    Usage:
        python -m app.cli get-paginated <limit> <offset>
    '''
    with get_session() as db:
        users = db.exec(select(User).limit(limit).offset(offset)).all() # select -> get table with column, limit -> max entries to return, offset -> how many entries to skip before starting to return results
        if not users:
            print("No users found with the given pagination parameters.")
            return
        for user in users:
            print(user)

if __name__ == "__main__":
    cli()