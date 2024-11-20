from app import db
from datetime import datetime
from sqlalchemy import Index

class Character(db.Model):
    __tablename__ = 'character'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    
    # Basic Info
    name = db.Column(db.String(100), nullable=False)
    race = db.Column(db.String(50), nullable=False)
    character_concept = db.Column(db.String(100), nullable=False)
    rank = db.Column(db.String(20), default='Novice')
    
    # Attributes (Savage Worlds uses die types)
    agility = db.Column(db.String(3), default='d4')
    smarts = db.Column(db.String(3), default='d4')
    spirit = db.Column(db.String(3), default='d4')
    strength = db.Column(db.String(3), default='d4')
    vigor = db.Column(db.String(3), default='d4')
    
    # Character Details
    hindrances = db.Column(db.Text)
    edges = db.Column(db.Text)
    equipment = db.Column(db.Text)
    money = db.Column(db.Integer, default=500)
    background = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = db.relationship('Campaign', back_populates='characters')
    
    def __repr__(self):
        return f'<Character {self.name}>'

# Create indexes for frequently queried fields
Index('idx_character_user_id', Character.user_id)
Index('idx_character_campaign_id', Character.campaign_id)
Index('idx_character_name', Character.name)
