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
    race = db.Column(db.String(50))
    character_class = db.Column(db.String(50))
    level = db.Column(db.Integer, default=1)
    background = db.Column(db.String(50))
    alignment = db.Column(db.String(50))
    experience_points = db.Column(db.Integer, default=0)
    strength = db.Column(db.Integer)
    dexterity = db.Column(db.Integer)
    constitution = db.Column(db.Integer)
    intelligence = db.Column(db.Integer)
    wisdom = db.Column(db.Integer)
    charisma = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add relationships
    inventory = db.relationship('CharacterInventory', backref='character', lazy=True)
    currency = db.relationship('CharacterCurrency', backref='character', uselist=False, lazy=True)

# Campaign model
class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    setting = db.Column(db.String(100))
    level_range = db.Column(db.String(50))
    max_players = db.Column(db.Integer, default=5)
    status = db.Column(db.String(20), default='draft')  # 'draft', 'active', or 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    next_session = db.Column(db.DateTime)
    members = db.relationship('User', secondary='campaign_members', backref='campaigns')
    notes = db.relationship('CampaignNote', backref='campaign', lazy=True)
    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_campaigns')

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
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    item_type = db.Column(db.String(50))  # weapon, armor, potion, etc.
    rarity = db.Column(db.String(50))  # common, uncommon, rare, very rare, legendary
    cost = db.Column(db.Integer)  # in copper pieces
    weight = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class CharacterInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    equipped = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)

class CharacterCurrency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    copper = db.Column(db.Integer, default=0)
    silver = db.Column(db.Integer, default=0)
    electrum = db.Column(db.Integer, default=0)
    gold = db.Column(db.Integer, default=0)
    platinum = db.Column(db.Integer, default=0)

class CampaignBannedItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    reason = db.Column(db.Text)
    banned_at = db.Column(db.DateTime, default=datetime.utcnow)
    banned_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

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
        character_class = request.form['class']
        race = request.form['race']
        level = int(request.form.get('level', 1))
        background = request.form.get('background', '')
        alignment = request.form.get('alignment', '')
        experience_points = int(request.form.get('experience_points', 0))
        strength = int(request.form['strength'])
        dexterity = int(request.form['dexterity'])
        constitution = int(request.form.get('constitution', 10))
        intelligence = int(request.form['intelligence'])
        wisdom = int(request.form.get('wisdom', 10))
        charisma = int(request.form.get('charisma', 10))

        if not all(1 <= stat <= 20 for stat in [strength, dexterity, constitution, intelligence, wisdom, charisma]):
            raise ValueError("All attributes must be between 1 and 20.")

        character = Character(
            user_id=current_user.id,
            name=name,
            character_class=character_class,
            race=race,
            level=level,
            background=background,
            alignment=alignment,
            experience_points=experience_points,
            strength=strength,
            dexterity=dexterity,
            constitution=constitution,
            intelligence=intelligence,
            wisdom=wisdom,
            charisma=charisma
        )
        db.session.add(character)
        db.session.commit()
        
        # Create default empty currency for the character
        currency = CharacterCurrency(
            character_id=character.id,
            copper=0,
            silver=0,
            electrum=0,
            gold=0,
            platinum=0
        )
        db.session.add(currency)
        db.session.commit()

        return jsonify({
            'message': 'Character saved successfully',
            'character': {
                'id': character.id,
                'name': character.name,
                'class': character.character_class,
                'race': character.race,
                'level': character.level,
                'strength': character.strength,
                'dexterity': character.dexterity,
                'constitution': character.constitution,
                'intelligence': character.intelligence,
                'wisdom': character.wisdom,
                'charisma': character.charisma
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
        campaign_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'setting': request.form.get('setting'),
            'level_range': request.form.get('level_range'),
            'max_players': int(request.form.get('max_players', 5)),
            'status': request.form.get('status', 'draft'),
            'owner_id': current_user.id
        }
        
        campaign = Campaign(
            name=campaign_data['name'],
            description=campaign_data['description'],
            setting=campaign_data['setting'],
            level_range=campaign_data['level_range'],
            max_players=campaign_data['max_players'],
            status=campaign_data['status'],
            owner_id=campaign_data['owner_id']
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
        campaign.level_range = data.get('level_range', campaign.level_range)
        campaign.max_players = data.get('max_players', campaign.max_players)
        campaign.status = data.get('status', campaign.status)
        
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

@app.route('/character/<int:character_id>/inventory')
@login_required
def character_inventory(character_id):
    character = Character.query.get_or_404(character_id)
    if character.user_id != current_user.id and not current_user.is_dm:
        flash('You do not have permission to view this inventory.', 'danger')
        return redirect(url_for('characters'))
    
    return render_template('character_inventory.html', character=character)

@app.route('/character/<int:character_id>/add_item', methods=['POST'])
@login_required
def add_item_to_character(character_id):
    character = Character.query.get_or_404(character_id)
    if character.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)
    equipped = data.get('equipped', False)
    notes = data.get('notes', '')
    
    # Check if item is banned in character's campaign
    if character.campaign:
        banned_item = CampaignBannedItems.query.filter_by(
            campaign_id=character.campaign.id,
            item_id=item_id
        ).first()
        if banned_item:
            return jsonify({
                'error': f'This item is banned in this campaign. Reason: {banned_item.reason}'
            }), 400
    
    # Get the item and check if it exists
    item = Item.query.get_or_404(item_id)
    
    # Check if character already has this item
    existing_item = CharacterInventory.query.filter_by(
        character_id=character_id,
        item_id=item_id
    ).first()
    
    if existing_item:
        existing_item.quantity += quantity
        existing_item.notes = notes if notes else existing_item.notes
    else:
        new_item = CharacterInventory(
            character_id=character_id,
            item_id=item_id,
            quantity=quantity,
            equipped=equipped,
            notes=notes
        )
        db.session.add(new_item)
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/character/<int:character_id>/remove_item/<int:inventory_id>', methods=['POST'])
@login_required
def remove_item(character_id, inventory_id):
    character = Character.query.get_or_404(character_id)
    if character.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    inventory_item = CharacterInventory.query.get_or_404(inventory_id)
    if inventory_item.character_id != character_id:
        return jsonify({'error': 'Invalid item'}), 400
        
    db.session.delete(inventory_item)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/character/<int:character_id>/toggle_equipped/<int:inventory_id>', methods=['POST'])
@login_required
def toggle_equipped(character_id, inventory_id):
    character = Character.query.get_or_404(character_id)
    if character.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    inventory_item = CharacterInventory.query.get_or_404(inventory_id)
    if inventory_item.character_id != character_id:
        return jsonify({'error': 'Invalid item'}), 400
        
    inventory_item.equipped = not inventory_item.equipped
    db.session.commit()
    return jsonify({'success': True})

@app.route('/character/<int:character_id>/update_currency', methods=['POST'])
@login_required
def update_currency(character_id):
    character = Character.query.get_or_404(character_id)
    if character.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    currency = character.currency
    if not currency:
        currency = CharacterCurrency(character_id=character.id)
        db.session.add(currency)
    
    currency.platinum = data.get('platinum', 0)
    currency.gold = data.get('gold', 0)
    currency.electrum = data.get('electrum', 0)
    currency.silver = data.get('silver', 0)
    currency.copper = data.get('copper', 0)
    
    db.session.commit()
    return jsonify({'success': True})

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
        
    currency = character.currency
    if not currency:
        currency = CharacterCurrency(character_id=character.id)
        db.session.add(currency)
        db.session.commit()
    
    return jsonify({
        'id': character.id,
        'name': character.name,
        'race': character.race,
        'class_type': character.character_class,
        'level': character.level,
        'strength': character.strength,
        'dexterity': character.dexterity,
        'constitution': character.constitution,
        'intelligence': character.intelligence,
        'wisdom': character.wisdom,
        'charisma': character.charisma,
        'inventory': inventory_items,
        'currency': {
            'platinum': currency.platinum,
            'gold': currency.gold,
            'electrum': currency.electrum,
            'silver': currency.silver,
            'copper': currency.copper
        }
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

if __name__ == '__main__':
    with app.app_context():
        while True:
            try:
                db.create_all()
                break
            except Exception as e:
                print(f"Error creating database: {e}. Retrying in 5 seconds...")
                time.sleep(5)
    app.run(debug=True)