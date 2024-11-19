from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os
import time
import random

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
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    name = db.Column(db.String(100), nullable=False)
    race = db.Column(db.String(50))  # For different races/ancestries in Savage Worlds
    rank = db.Column(db.String(50), default='Novice')  # Novice, Seasoned, Veteran, Heroic, Legendary
    experience_points = db.Column(db.Integer, default=0)
    
    # Attributes
    agility = db.Column(db.String(10), default='d6')  # Stored as 'd4', 'd6', etc.
    smarts = db.Column(db.String(10), default='d6')
    spirit = db.Column(db.String(10), default='d6')
    strength = db.Column(db.String(10), default='d6')
    vigor = db.Column(db.String(10), default='d6')
    
    # Derived Stats
    pace = db.Column(db.Integer, default=6)
    parry = db.Column(db.Integer, default=2)  # 2 + Fighting/2
    toughness = db.Column(db.Integer, default=4)  # 2 + Vigor/2
    charisma = db.Column(db.Integer, default=0)
    
    # Character Concept
    concept = db.Column(db.String(500))  # Character concept/archetype
    hindrances = db.Column(db.String(1000))  # Major and Minor Hindrances
    edges = db.Column(db.String(1000))  # Character Edges
    
    # Skills (stored as JSON strings)
    core_skills = db.Column(db.String(1000))  # Core skills like Fighting, Shooting, etc.
    knowledge_skills = db.Column(db.String(1000))  # Knowledge-based skills
    
    # Powers and Special Abilities
    powers = db.Column(db.String(1000))  # For characters with Arcane Backgrounds
    power_points = db.Column(db.Integer, default=0)
    
    # Gear and Resources
    money = db.Column(db.Integer, default=500)  # Starting money in campaign currency
    
    # Wounds and Status
    wounds = db.Column(db.Integer, default=0)  # 0-3 wounds before Incapacitated
    fatigue = db.Column(db.Integer, default=0)  # 0-2 fatigue levels
    bennies = db.Column(db.Integer, default=3)  # Refresh each session
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    inventory = db.relationship('CharacterInventory', backref='character_ref', lazy=True)

# Campaign model
class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    setting = db.Column(db.String(100))  # e.g., Deadlands, Rifts, Fantasy, etc.
    
    # Campaign Rules
    power_level = db.Column(db.String(50), default='Novice')  # Starting power level
    available_races = db.Column(db.String(1000))  # List of allowed races
    available_edges = db.Column(db.String(1000))  # List of allowed edges
    house_rules = db.Column(db.Text)  # Custom rules for this campaign
    
    # Campaign Status
    status = db.Column(db.String(20), default='draft')  # 'draft', 'active', or 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    next_session = db.Column(db.DateTime)
    
    # Starting Resources
    starting_money = db.Column(db.Integer, default=500)
    starting_bennies = db.Column(db.Integer, default=3)
    
    # Campaign Features
    use_powers = db.Column(db.Boolean, default=True)  # Whether magical powers are allowed
    use_guns = db.Column(db.Boolean, default=True)  # Whether firearms are available
    use_vehicles = db.Column(db.Boolean, default=True)  # Whether vehicles are available
    
    # New field: max_players
    max_players = db.Column(db.Integer, default=4)
    
    # Relationships
    members = db.relationship('User', secondary='campaign_members', backref='campaigns')
    notes = db.relationship('CampaignNote', backref='campaign', lazy=True)
    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_campaigns')

# Item model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, default=0)
    item_type = db.Column(db.String(50), nullable=False)  # Weapon, Armor, Gear, etc.
    
    # Weapon Stats
    damage = db.Column(db.String(20))  # e.g., "2d6+2" for weapons
    range = db.Column(db.String(20))  # Range increments for ranged weapons
    ap = db.Column(db.Integer)  # Armor Piercing value
    rof = db.Column(db.Integer, default=1)  # Rate of Fire
    shots = db.Column(db.Integer)  # Ammunition capacity
    min_str = db.Column(db.String(10))  # Minimum Strength die type required
    
    # Armor Stats
    armor = db.Column(db.Integer)  # Armor bonus
    coverage = db.Column(db.String(50))  # What body parts it covers
    
    # General Properties
    cost = db.Column(db.Integer)  # Cost in campaign currency
    notes = db.Column(db.Text)  # Special rules or effects

# Campaign Notes model for DM notes and session summaries
class CampaignNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    note_type = db.Column(db.String(50))  # session_summary, dm_note, player_note
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Map model
class Map(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    map_type = db.Column(db.String(50), nullable=False)
    grid_width = db.Column(db.Integer, nullable=False)
    grid_height = db.Column(db.Integer, nullable=False)
    background_color = db.Column(db.String(7), nullable=False)  # hex color
    show_grid = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=True)
    
    # Add relationship to creator
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_maps')

# Item and Inventory Models
class CharacterInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    equipped = db.Column(db.Boolean, default=False)
    
    item = db.relationship('Item')

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
        rank = request.form['rank']
        race = request.form['race']
        experience_points = int(request.form.get('experience_points', 0))
        
        # Get attributes
        agility = request.form.get('agility', 'd6')
        smarts = request.form.get('smarts', 'd6')
        spirit = request.form.get('spirit', 'd6')
        strength = request.form.get('strength', 'd6')
        vigor = request.form.get('vigor', 'd6')
        
        # Get derived stats
        pace = int(request.form.get('pace', 6))
        parry = int(request.form.get('parry', 2))
        toughness = int(request.form.get('toughness', 4))
        charisma = int(request.form.get('charisma', 0))
        
        # Get character concept
        concept = request.form.get('concept', '')
        hindrances = request.form.get('hindrances', '')
        edges = request.form.get('edges', '')
        
        # Get skills
        core_skills = request.form.get('core_skills', '')
        knowledge_skills = request.form.get('knowledge_skills', '')
        
        # Get powers and special abilities
        powers = request.form.get('powers', '')
        power_points = int(request.form.get('power_points', 0))
        
        # Get gear and resources
        money = int(request.form.get('money', 500))
        
        # Get wounds and status
        wounds = int(request.form.get('wounds', 0))
        fatigue = int(request.form.get('fatigue', 0))
        bennies = int(request.form.get('bennies', 3))

        character = Character(
            user_id=current_user.id,
            name=name,
            rank=rank,
            race=race,
            experience_points=experience_points,
            agility=agility,
            smarts=smarts,
            spirit=spirit,
            strength=strength,
            vigor=vigor,
            pace=pace,
            parry=parry,
            toughness=toughness,
            charisma=charisma,
            concept=concept,
            hindrances=hindrances,
            edges=edges,
            core_skills=core_skills,
            knowledge_skills=knowledge_skills,
            powers=powers,
            power_points=power_points,
            money=money,
            wounds=wounds,
            fatigue=fatigue,
            bennies=bennies
        )
        db.session.add(character)
        db.session.commit()
        
        return jsonify({
            'message': 'Character saved successfully',
            'character': {
                'id': character.id,
                'name': character.name,
                'rank': character.rank,
                'race': character.race,
                'experience_points': character.experience_points,
                'agility': character.agility,
                'smarts': character.smarts,
                'spirit': character.spirit,
                'strength': character.strength,
                'vigor': character.vigor,
                'pace': character.pace,
                'parry': character.parry,
                'toughness': character.toughness,
                'charisma': character.charisma,
                'concept': character.concept,
                'hindrances': character.hindrances,
                'edges': character.edges,
                'core_skills': character.core_skills,
                'knowledge_skills': character.knowledge_skills,
                'powers': character.powers,
                'power_points': character.power_points,
                'money': character.money,
                'wounds': character.wounds,
                'fatigue': character.fatigue,
                'bennies': character.bennies
            }
        })
    except ValueError as e:
        return jsonify({'message': 'Error saving character', 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred', 'error': str(e)}), 500

@app.route('/characters')
@login_required
def view_characters():
    characters = Character.query.filter_by(user_id=current_user.id).all()
    return render_template('characters.html', characters=characters)

@app.route('/campaigns_page')
@login_required
def campaigns_page():
    user_campaigns = Campaign.query.filter_by(owner_id=current_user.id).all()
    return render_template('campaigns.html', campaigns=user_campaigns)

@app.route('/campaign/<int:campaign_id>')
@login_required
def campaign_details(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Check access first
    if current_user not in campaign.members and current_user.id != campaign.owner_id:
        flash('You do not have access to this campaign.', 'error')
        return redirect(url_for('participating_campaigns'))
    
    # Get characters for players in the campaign
    campaign_characters = Character.query.join(
        User, Character.user_id == User.id
    ).join(
        campaign_members, User.id == campaign_members.c.user_id
    ).filter(
        campaign_members.c.campaign_id == campaign_id
    ).all()
    
    return render_template('campaign_details.html', 
                         campaign=campaign,
                         campaign_characters=campaign_characters)

@app.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    if request.method == 'POST':
        data = request.get_json()
        campaign_data = {
            'name': data.get('name'),
            'description': data.get('description'),
            'setting': data.get('setting'),
            'power_level': data.get('power_level', 'Novice'),
            'available_races': data.get('available_races', ''),
            'available_edges': data.get('available_edges', ''),
            'house_rules': data.get('house_rules', ''),
            'starting_money': int(data.get('starting_money', 500)),
            'starting_bennies': int(data.get('starting_bennies', 3)),
            'use_powers': data.get('use_powers', True),
            'use_guns': data.get('use_guns', True),
            'use_vehicles': data.get('use_vehicles', True),
            'owner_id': current_user.id,
            'max_players': data.get('max_players', 4)
        }
        
        try:
            campaign = Campaign(
                name=campaign_data['name'],
                description=campaign_data['description'],
                setting=campaign_data['setting'],
                power_level=campaign_data['power_level'],
                available_races=campaign_data['available_races'],
                available_edges=campaign_data['available_edges'],
                house_rules=campaign_data['house_rules'],
                starting_money=campaign_data['starting_money'],
                starting_bennies=campaign_data['starting_bennies'],
                use_powers=campaign_data['use_powers'],
                use_guns=campaign_data['use_guns'],
                use_vehicles=campaign_data['use_vehicles'],
                owner_id=campaign_data['owner_id'],
                max_players=campaign_data['max_players']
            )
            
            db.session.add(campaign)
            db.session.commit()
            
            response_data = {
                'success': True,
                'message': 'Campaign created successfully!',
                'campaign': {
                    'id': campaign.id,
                    'name': campaign.name
                }
            }
            return jsonify(response_data)
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    
    return render_template('create_campaign.html')

@app.route('/campaign/<int:campaign_id>/update', methods=['POST'])
@login_required
def update_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if current_user.id != campaign.owner_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        campaign.name = data.get('name', campaign.name)
        campaign.description = data.get('description', campaign.description)
        campaign.setting = data.get('setting', campaign.setting)
        campaign.power_level = data.get('power_level', campaign.power_level)
        campaign.available_races = data.get('available_races', campaign.available_races)
        campaign.available_edges = data.get('available_edges', campaign.available_edges)
        campaign.house_rules = data.get('house_rules', campaign.house_rules)
        campaign.starting_money = data.get('starting_money', campaign.starting_money)
        campaign.starting_bennies = data.get('starting_bennies', campaign.starting_bennies)
        campaign.use_powers = data.get('use_powers', campaign.use_powers)
        campaign.use_guns = data.get('use_guns', campaign.use_guns)
        campaign.use_vehicles = data.get('use_vehicles', campaign.use_vehicles)
        
        next_session = data.get('next_session')
        if next_session:
            campaign.next_session = datetime.fromisoformat(next_session)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Campaign updated successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/campaign/<int:campaign_id>/update_status', methods=['POST'])
@login_required
def update_campaign_status(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner_id != current_user.id:
        flash('You do not have permission to update this campaign.', 'danger')
        return redirect(url_for('campaign_details', campaign_id=campaign_id))
    
    new_status = request.form.get('status')
    if new_status in ['draft', 'active', 'completed']:
        campaign.status = new_status
        db.session.commit()
        flash(f'Campaign status updated to {new_status}.', 'success')
    else:
        flash('Invalid status provided.', 'danger')
    
    return redirect(url_for('campaign_details', campaign_id=campaign_id))

@app.route('/campaign/<int:campaign_id>/add_note', methods=['POST'])
@login_required
def add_campaign_note(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if current_user not in campaign.members and current_user.id != campaign.owner_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        note = CampaignNote(
            campaign_id=campaign_id,
            title=data['title'],
            content=data['content'],
            note_type=data['note_type'],
            created_by=current_user.id
        )
        
        db.session.add(note)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Note added successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/participating_campaigns')
@login_required
def participating_campaigns():
    # Get campaigns where user is either a member or owner
    participating = Campaign.query.filter(
        db.or_(
            Campaign.members.any(id=current_user.id),
            Campaign.owner_id == current_user.id
        )
    ).all()
    
    # Get available campaigns where user is not a member
    available = Campaign.query.filter(
        db.and_(
            Campaign.owner_id != current_user.id,
            ~Campaign.members.any(id=current_user.id)
        )
    ).all()
    
    return render_template('participating_campaigns.html', 
                         campaigns=participating,
                         available_campaigns=available)

@app.route('/campaign/<int:campaign_id>/join', methods=['POST'])
@login_required
def join_campaign(campaign_id):
    if not current_user.is_authenticated:
        flash('You must be logged in to join a campaign.', 'error')
        return redirect(url_for('login'))
    
    campaign = Campaign.query.get_or_404(campaign_id)
    character_id = request.form.get('character_id')
    
    if character_id:
        character = Character.query.get_or_404(character_id)
        if character.user_id != current_user.id:
            flash('You can only select your own characters.', 'error')
            return redirect(url_for('campaign_details', campaign_id=campaign_id))
        
        # Update character's campaign
        character.campaign_id = campaign_id
        db.session.commit()
        flash(f'Your character {character.name} has joined the campaign!', 'success')
    
    # Add user to campaign members if not already a member
    if current_user not in campaign.members:
        campaign.members.append(current_user)
        db.session.commit()
        flash('You have successfully joined the campaign!', 'success')
    
    return redirect(url_for('campaign_details', campaign_id=campaign_id))

@app.route('/campaign/<int:campaign_id>/select-character', methods=['GET'])
@login_required
def select_character(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    available_characters = Character.query.filter_by(
        user_id=current_user.id,
        campaign_id=None
    ).all()
    return render_template('select_character.html', 
                         campaign=campaign,
                         characters=available_characters)

@app.route('/dice_roll', methods=['POST'])
@login_required
def dice_roll():
    dice_type = request.form.get('dice_type', 'd20')
    modifier = int(request.form.get('modifier', 0))
    
    # Add dice rolling logic here
    result = random.randint(1, int(dice_type[1:])) + modifier
    return jsonify({'roll': result})

@app.route('/campaign/<int:campaign_id>/remove_member/<int:user_id>', methods=['POST'])
@login_required
def remove_campaign_member(campaign_id, user_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if current_user.id != campaign.owner_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        if user in campaign.members:
            campaign.members.remove(user)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'Successfully removed {user.username} from the campaign.'
            })
        return jsonify({
            'success': False,
            'message': 'User is not a member of this campaign.'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/create_map', methods=['POST'])
@login_required
def create_map():
    try:
        # Validate required fields
        name = request.form.get('name')
        map_type = request.form.get('map_type')
        if not name or not map_type:
            raise ValueError("Name and map type are required")

        # Get optional campaign_id
        campaign_id = request.form.get('campaign_id')
        if campaign_id:
            campaign = Campaign.query.get(campaign_id)
            if not campaign or campaign.owner_id != current_user.id:
                raise ValueError("Invalid campaign ID or you don't have permission")

        # Create map
        map_data = Map(
            name=name,
            map_type=map_type,
            grid_width=int(request.form.get('grid_width', 20)),
            grid_height=int(request.form.get('grid_height', 20)),
            background_color=request.form.get('background_color', '#ffffff'),
            show_grid=request.form.get('show_grid', 'true').lower() == 'true',
            created_by=current_user.id,
            campaign_id=campaign_id
        )
        
        db.session.add(map_data)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Map created successfully!',
            'map': {
                'id': map_data.id,
                'name': map_data.name,
                'type': map_data.map_type,
                'grid_width': map_data.grid_width,
                'grid_height': map_data.grid_height
            }
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f"An error occurred: {str(e)}"
        }), 500

@app.route('/map/<int:map_id>')
@login_required
def view_map(map_id):
    map_data = Map.query.get_or_404(map_id)
    
    # Check permissions
    if map_data.campaign_id:
        campaign = Campaign.query.get(map_data.campaign_id)
        if campaign.owner_id != current_user.id and current_user not in campaign.members:
            flash('You do not have permission to view this map.', 'danger')
            return redirect(url_for('home'))
    elif map_data.created_by != current_user.id:
        flash('You do not have permission to view this map.', 'danger')
        return redirect(url_for('home'))
    
    return render_template('map_view.html', map=map_data)

@app.route('/items')
@login_required
def items():
    items = Item.query.all()
    return render_template('items.html', items=items)

# Inventory Management Routes
@app.route('/character/<int:character_id>/inventory/add', methods=['POST'])
@login_required
def add_item_to_inventory(character_id):
    character = Character.query.get_or_404(character_id)
    if character.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        item = Item(
            name=data['name'],
            weight=float(data['weight']),
            item_type=data['item_type']
        )
        db.session.add(item)
        db.session.commit()
        
        inventory_item = CharacterInventory(
            character_id=character_id,
            item_id=item.id,
            quantity=int(data['quantity']),
            equipped=False
        )
        db.session.add(inventory_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item added successfully',
            'item': {
                'id': item.id,
                'name': item.name,
                'weight': item.weight,
                'quantity': inventory_item.quantity
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/character/<int:character_id>/inventory/<int:inventory_id>/remove', methods=['POST'])
@login_required
def remove_inventory_item(character_id, inventory_id):
    character = Character.query.get_or_404(character_id)
    if character.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        inventory_item = CharacterInventory.query.get_or_404(inventory_id)
        if inventory_item.character_id != character_id:
            return jsonify({'success': False, 'message': 'Item not found'}), 404
        
        db.session.delete(inventory_item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Item removed successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/character/<int:character_id>/inventory/<int:inventory_id>/toggle-equipped', methods=['POST'])
@login_required
def toggle_item_equipped(character_id, inventory_id):
    character = Character.query.get_or_404(character_id)
    if character.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        inventory_item = CharacterInventory.query.get_or_404(inventory_id)
        if inventory_item.character_id != character_id:
            return jsonify({'success': False, 'message': 'Item not found'}), 404
        
        # Toggle equipped status
        inventory_item.equipped = not inventory_item.equipped
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Item {"equipped" if inventory_item.equipped else "unequipped"} successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/character/<int:character_id>/inventory', methods=['GET'])
@login_required
def get_inventory(character_id):
    character = Character.query.get_or_404(character_id)
    if character.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    inventory_items = []
    for inv in character.inventory:
        item = Item.query.get(inv.item_id)
        inventory_items.append({
            'id': inv.id,
            'name': item.name,
            'quantity': inv.quantity,
            'weight': item.weight,
            'equipped': inv.equipped,
            'item_type': item.item_type
        })
    
    return jsonify({
        'success': True,
        'inventory': inventory_items,
        'total_weight': sum(item['weight'] * item['quantity'] for item in inventory_items)
    })

@app.route('/character/<int:character_id>')
@login_required
def get_character(character_id):
    character = Character.query.get_or_404(character_id)
    if character.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    inventory_items = []
    for inv in character.inventory:
        item = Item.query.get(inv.item_id)
        inventory_items.append({
            'id': inv.id,
            'name': item.name,
            'quantity': inv.quantity,
            'weight': item.weight,
            'equipped': inv.equipped,
            'notes': inv.notes
        })
        
    return jsonify({
        'id': character.id,
        'name': character.name,
        'rank': character.rank,
        'race': character.race,
        'experience_points': character.experience_points,
        'agility': character.agility,
        'smarts': character.smarts,
        'spirit': character.spirit,
        'strength': character.strength,
        'vigor': character.vigor,
        'pace': character.pace,
        'parry': character.parry,
        'toughness': character.toughness,
        'charisma': character.charisma,
        'concept': character.concept,
        'hindrances': character.hindrances,
        'edges': character.edges,
        'core_skills': character.core_skills,
        'knowledge_skills': character.knowledge_skills,
        'powers': character.powers,
        'power_points': character.power_points,
        'money': character.money,
        'wounds': character.wounds,
        'fatigue': character.fatigue,
        'bennies': character.bennies,
        'inventory': inventory_items
    })

@app.route('/campaign/<int:campaign_id>/banned_items')
@login_required
def get_banned_items(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    banned_items = []
    for banned in CampaignBannedItems.query.filter_by(campaign_id=campaign_id).all():
        item = Item.query.get(banned.item_id)
        banned_by = User.query.get(banned.banned_by)
        banned_items.append({
            'id': banned.id,
            'name': item.name,
            'reason': banned.reason,
            'banned_by_name': banned_by.username
        })
    
    return jsonify(banned_items)

@app.route('/character/<int:character_id>/details')
@login_required
def character_details(character_id):
    character = Character.query.get_or_404(character_id)
    if character.user_id != current_user.id:
        flash('You do not have permission to view this character.', 'error')
        return redirect(url_for('characters'))
    return render_template('character_details.html', character=character)

@app.route('/campaign/<int:campaign_id>/banned_items')
@login_required
def campaign_banned_items(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner_id != current_user.id:
        flash('Only the DM can manage banned items.', 'danger')
        return redirect(url_for('campaign_details', campaign_id=campaign_id))
    
    banned_items = CampaignBannedItems.query.filter_by(campaign_id=campaign_id).all()
    all_items = Item.query.all()
    return render_template('campaign_banned_items.html', 
                         campaign=campaign, 
                         banned_items=banned_items,
                         all_items=all_items)

@app.route('/campaign/<int:campaign_id>/ban_item', methods=['POST'])
@login_required
def ban_item(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    item_id = data.get('item_id')
    reason = data.get('reason', '')
    
    # Check if item is already banned
    existing = CampaignBannedItems.query.filter_by(
        campaign_id=campaign_id,
        item_id=item_id
    ).first()
    
    if existing:
        return jsonify({'error': 'Item is already banned'}), 400
    
    banned_item = CampaignBannedItems(
        campaign_id=campaign_id,
        item_id=item_id,
        reason=reason,
        banned_by=current_user.id
    )
    db.session.add(banned_item)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/campaign/<int:campaign_id>/unban_item/<int:banned_item_id>', methods=['POST'])
@login_required
def unban_item(campaign_id, banned_item_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    banned_item = CampaignBannedItems.query.get_or_404(banned_item_id)
    if banned_item.campaign_id != campaign_id:
        return jsonify({'error': 'Invalid banned item'}), 400
        
    db.session.delete(banned_item)
    db.session.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create all database tables
        print("Database tables created successfully!")
        app.run(debug=True)