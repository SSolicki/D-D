from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler
from app import create_app, db
import click

# Load environment variables from .env file
load_dotenv()

app = create_app()

@app.cli.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    from app.models.database import init_db
    init_db()
    click.echo('Initialized the database.')

@app.cli.command("reset-db")
@click.confirmation_option(prompt='Are you sure you want to reset the database?')
def reset_db_command():
    """Reset the database (WARNING: This will delete all data!)"""
    from app.models.database import reset_db
    reset_db()
    click.echo('Reset the database.')

@app.cli.command("clean-db")
@click.confirmation_option(prompt='This will delete ALL existing tables. Are you sure?')
def clean_db_command():
    """Remove all tables from the database."""
    with app.app_context():
        import sqlite3
        from flask import current_app
        
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if db_path.startswith('/'):
            db_path = db_path[1:]
        
        try:
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            # Drop each table
            for table in tables:
                if table[0] != 'sqlite_sequence':  # Don't drop sqlite_sequence
                    cursor.execute(f"DROP TABLE IF EXISTS {table[0]};")
            
            conn.commit()
            conn.close()
            click.echo('Successfully removed all tables.')
        except Exception as e:
            click.echo(f'Error: {str(e)}')
            if conn:
                conn.close()

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                os.path.join(os.path.expanduser('~'), 'dnd_app.log'),
                mode='a'
            )
        ]
    )
    
    app.logger.info('D&D App startup')
    app.run(debug=True)
