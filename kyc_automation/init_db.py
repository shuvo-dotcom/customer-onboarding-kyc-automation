from app.core.init_db import init_db

if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Database tables created successfully.") 