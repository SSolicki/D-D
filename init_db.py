from DnDapp import app, db

# Create the database and tables
with app.app_context():
    db.drop_all()  # Drop all existing tables
    db.create_all()  # Create all tables
    print("Database initialized successfully!")
