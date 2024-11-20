from app import create_app, db
import click

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    click.echo('Dropping all tables...')
    db.drop_all()
    click.echo('Creating all tables...')
    db.create_all()
    click.echo('Database initialized successfully!')

if __name__ == '__main__':
    app.run(debug=True)
