#!/usr/bin/env python3
import typer
from getpass import getpass
from bot.database import Database

app = typer.Typer(help="User management CLI for your bot")

def ensure_table():
    with Database() as db:
        db.ensure_user_table()

@app.command()
def init():
    """Create the users table (if not exists)."""
    ensure_table()
    typer.secho("✅ User table ensured.", fg=typer.colors.GREEN)

@app.command()
def add(username: str = typer.Option(..., prompt=True, help="Username to add")):
    """Add a new user; you’ll be prompted for password."""
    ensure_table()
    password = getpass("Password: ")
    if not password:
        raise typer.BadParameter("Password cannot be empty")
    with Database() as db:
        if db.add_user(username, password):
            typer.secho(f"User '{username}' added.", fg=typer.colors.GREEN)
        else:
            typer.secho(f"User '{username}' already exists.", fg=typer.colors.YELLOW)

@app.command()
def list():
    """List all users."""
    ensure_table()
    with Database() as db:
        users = db.list_users()
    if users:
        for user_id, uname, created in users:
            typer.echo(f"{user_id}\t{uname}\t{created}")
    else:
        typer.echo("No users found.")

@app.command()
def update(username: str = typer.Argument(...), new_password: str = None):
    """
    Update a user’s password. If --new-password not passed, you’ll be prompted.
    """
    ensure_table()
    pwd = new_password or getpass("New password: ")
    if not pwd:
        raise typer.BadParameter("Password cannot be empty")
    with Database() as db:
        if db.update_password(username, pwd):
            typer.secho(f"Password updated for '{username}'.", fg=typer.colors.GREEN)
        else:
            typer.secho(f"User '{username}' not found.", fg=typer.colors.RED)

@app.command()
def delete(username: str = typer.Argument(...)):
    """Delete a user by username."""
    ensure_table()
    confirm = typer.confirm(f"Are you sure you want to delete '{username}'?")
    if not confirm:
        raise typer.Abort()
    with Database() as db:
        if db.delete_user(username):
            typer.secho(f"User '{username}' deleted.", fg=typer.colors.GREEN)
        else:
            typer.secho(f"User '{username}' not found.", fg=typer.colors.RED)

if __name__ == "__main__":
    app()