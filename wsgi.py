from app import app, init_db

# Initialize database tables on server launch
init_db()

if __name__ == "__main__":
    app.run()
