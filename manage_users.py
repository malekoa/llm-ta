import argparse
from bot.database import Database

def main():
    parser = argparse.ArgumentParser(description="User management CLI")
    parser.add_argument("action", choices=["init", "add", "list", "update", "delete"])
    parser.add_argument("--username", help="Username")
    parser.add_argument("--password", help="Password")
    args = parser.parse_args()

    with Database() as db:
        db.ensure_user_table()

        if args.action == "init":
            print("User table ensured.")
        elif args.action == "add":
            if not args.username or not args.password:
                print("Username and password required.")
            elif db.add_user(args.username, args.password):
                print(f"User '{args.username}' added.")
            else:
                print(f"User '{args.username}' already exists.")
        elif args.action == "list":
            for user in db.list_users():
                print(user)
        elif args.action == "update":
            if not args.username or not args.password:
                print("Username and password required.")
            elif db.update_password(args.username, args.password):
                print(f"Password updated for '{args.username}'.")
            else:
                print(f"User '{args.username}' not found.")
        elif args.action == "delete":
            if not args.username:
                print("Username required.")
            elif db.delete_user(args.username):
                print(f"User '{args.username}' deleted.")
            else:
                print(f"User '{args.username}' not found.")

if __name__ == "__main__":
    main()