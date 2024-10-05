# D&D Web App

## Overview

The D&D Web App is a Flask-based web application designed for players and Dungeon Masters (DMs) to manage their Dungeons & Dragons (D&D) campaigns. Users can create characters, join campaigns, collaborate with others, and access a battle map to enhance their D&D gaming experience. The application features user authentication, character creation, campaign management, and secure data storage.

## Features

- **User Registration & Authentication**: Users can register, log in, and manage their accounts securely.
- **Character Creation**: Players can create and save their D&D characters, including attributes such as class, race, strength, dexterity, and intelligence.
- **Campaign Management**: Users can create, join, and view campaigns. DMs can manage their own campaigns.
- **Battle Map**: A feature for players and DMs to visualize battles and track progress.
- **Dice Rolling**: A dice-rolling feature that allows players to simulate D&D dice rolls.

## Tech Stack

- **Backend**: Python, Flask, Flask-Login, SQLAlchemy
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Database**: SQLite (for development purposes), PostgreSQL (for production)
- **Deployment**: Azure App Service, Azure Pipelines for CI/CD

## Prerequisites

- Python 3.8 or higher
- Virtualenv (recommended for creating a virtual environment)
- SQLite (comes by default with Python)
- Azure account (for deployment)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/dnd-web-app.git
   cd dnd-web-app
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Database**

   - Run the following commands to create the database:

   ```python
   from app import db
   db.create_all()
   ```

   - Alternatively, use Alembic to manage database migrations in production.

5. **Run the Application**

   ```bash
   flask run
   ```

   The application will be available at `http://127.0.0.1:5000`.

## Deployment

### Azure App Service

1. **Create an Azure App Service**
   - Go to the **Azure Portal** and create a new **Web App**.
   - Select **Linux** as the operating system and **Python** as the runtime stack.

2. **Set Up CI/CD with Azure Pipelines**
   - In **Azure DevOps**, create a new pipeline and link it to your repository.
   - Use the provided `.azure-pipelines.yml` file to automate the build and deployment process.

3. **Environment Variables**
   - In the Azure Portal, navigate to your Web App's **Configuration** section.
   - Add environment variables such as `SECRET_KEY` and database connection strings.

## Usage

- **Register** a new account.
- **Log in** with your account credentials.
- **Create characters** and assign attributes.
- **Create and manage campaigns** as a Dungeon Master.
- **Join campaigns** and collaborate with other players.
- **Access the battle map** and use the dice-rolling feature during sessions.

## Security Notes

- Ensure that the `SECRET_KEY` is updated to a strong value in the production environment.
- Passwords are hashed using `pbkdf2:sha256` for enhanced security.
- Use **Azure Key Vault** to store sensitive information like `SECRET_KEY` and database credentials.
- Consider deploying the app with a WSGI server like **Gunicorn** for production use.

## Planned Features

- **Character Sheet Export**: Ability to export characters as PDFs.
- **Real-Time Battle Map Updates**: Enable real-time updates to the battle map for all users.
- **Campaign Chat**: Add a chat feature for players in the same campaign.

## Contributing

Contributions are welcome! To contribute:

1. **Fork the repository**.
2. **Create a new branch** (`git checkout -b feature-branch`).
3. **Make your changes and commit** (`git commit -m 'Add new feature'`).
4. **Push to the branch** (`git push origin feature-branch`).
5. **Open a Pull Request**.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgements

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Bootstrap Documentation](https://getbootstrap.com/)
- [Azure Documentation](https://docs.microsoft.com/en-us/azure/)
- Dungeons & Dragons® is a registered trademark of Wizards of the Coast.

## Contact

For questions or support, please contact **simen.solicki@gmail.com**.