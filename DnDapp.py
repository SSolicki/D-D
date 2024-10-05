from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key in production.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dnd_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Character model
class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    class_type = db.Column(db.String(50), nullable=False)
    race = db.Column(db.String(50), nullable=False)
    strength = db.Column(db.Integer, nullable=False)
    dexterity = db.Column(db.Integer, nullable=False)
    intelligence = db.Column(db.Integer, nullable=False)

# Campaign model
class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    members = db.relationship('User', secondary='campaign_members', backref='campaigns')

campaign_members = db.Table('campaign_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('campaign_id', db.Integer, db.ForeignKey('campaign.id'), primary_key=True)
)

# Use Alembic for managing database migrations in production environments.

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email is already registered. Please log in or use a different email.', 'danger')
            return redirect(url_for('register'))

        # Proceed with creating the new user if the email doesn't exist
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        new_user = User(username=username, email=email, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while registering. Please try again.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful.', 'success')
            return redirect(url_for('home'))
        flash('Login failed. Please check your email and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/character_creation')
@login_required
def character_creation():
    return render_template('character_creation.html')

@app.route('/save_character', methods=['POST'])
@login_required
def save_character():
    # Server-side validation
    try:
        name = request.form['name']
        class_type = request.form['class']
        race = request.form['race']
        strength = int(request.form['strength'])
        dexterity = int(request.form['dexterity'])
        intelligence = int(request.form['intelligence'])

        if not (1 <= strength <= 20 and 1 <= dexterity <= 20 and 1 <= intelligence <= 20):
            raise ValueError("Attributes must be between 1 and 20.")

        character_data = Character(
            user_id=current_user.id,
            name=name,
            class_type=class_type,
            race=race,
            strength=strength,
            dexterity=dexterity,
            intelligence=intelligence
        )
        db.session.add(character_data)
        db.session.commit()
        return jsonify({'message': 'Character saved successfully', 'character': {
            'name': character_data.name,
            'class': character_data.class_type,
            'race': character_data.race,
            'strength': character_data.strength,
            'dexterity': character_data.dexterity,
            'intelligence': character_data.intelligence
        }})
    except ValueError as e:
        return jsonify({'message': 'Error saving character', 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred', 'error': str(e)}), 500

@app.route('/characters')
@login_required
def view_characters():
    characters = Character.query.filter_by(user_id=current_user.id).all()
    return render_template('characters.html', characters=characters)

@app.route('/campaigns')
@login_required
def campaigns_page():
    return render_template('campaigns.html')

@app.route('/create_campaign', methods=['POST'])
@login_required
def create_campaign():
    campaign_data = Campaign(
        owner_id=current_user.id,
        name=request.form['name'],
        description=request.form['description']
    )
    db.session.add(campaign_data)
    db.session.commit()
    return jsonify({'message': 'Campaign created successfully', 'campaign': {
        'name': campaign_data.name,
        'description': campaign_data.description
    }})

@app.route('/participating_campaigns')
@login_required
def participating_campaigns():
    campaigns = Campaign.query.filter(Campaign.members.any(id=current_user.id)).all()
    return render_template('participating_campaigns.html', campaigns=campaigns)

@app.route('/join_campaign/<int:campaign_id>')
@login_required
def join_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if campaign and current_user not in campaign.members:
        campaign.members.append(current_user)
        db.session.commit()
        flash('Successfully joined the campaign.', 'success')
    else:
        flash('Failed to join the campaign.', 'danger')
    return redirect(url_for('participating_campaigns'))

@app.route('/battle_map')
@login_required
def battle_map():
    return render_template('battle_map.html')

@app.route('/update_battle_map', methods=['POST'])
@login_required
def update_battle_map():
    map_data = request.get_json()
    return jsonify({'message': 'Battle map updated successfully'})

@app.route('/dice_roll', methods=['GET'])
@login_required
def dice_roll():
    import random
    dice_type = request.args.get('type', 'd20')
    dice_max = int(dice_type[1:]) if dice_type.startswith('d') else 20
    result = random.randint(1, dice_max)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)