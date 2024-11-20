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
    character_class = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, default=1)
    background = db.Column(db.String(100))
    alignment = db.Column(db.String(20))
    
    # Ability Scores
    strength = db.Column(db.String(10), default='10')
    dexterity = db.Column(db.String(10), default='10')
    constitution = db.Column(db.String(10), default='10')
    intelligence = db.Column(db.String(10), default='10')
    wisdom = db.Column(db.String(10), default='10')
    charisma = db.Column(db.String(10), default='10')
    
    # Game Stats
    experience_points = db.Column(db.Integer, default=0)
    hit_points = db.Column(db.Integer)
    armor_class = db.Column(db.Integer)
    initiative = db.Column(db.Integer)
    speed = db.Column(db.Integer, default=30)
    
    # Equipment and Resources
    equipment = db.Column(db.Text)
    gold = db.Column(db.Integer, default=0)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = db.relationship('Campaign', backref=db.backref('characters', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Character {self.name}>'
    
    def calculate_modifier(self, score):
        """Calculate ability score modifier."""
        score = int(score)
        return (score - 10) // 2
    
    def calculate_proficiency_bonus(self):
        """Calculate proficiency bonus based on level."""
        return (self.level - 1) // 4 + 2
    
    def calculate_hit_points(self):
        """Calculate max hit points."""
        con_mod = self.calculate_modifier(self.constitution)
        return (8 + con_mod) + ((self.level - 1) * (5 + con_mod))
    
    def calculate_armor_class(self):
        """Calculate base armor class."""
        return 10 + self.calculate_modifier(self.dexterity)
    
    def calculate_initiative(self):
        """Calculate initiative modifier."""
        return self.calculate_modifier(self.dexterity)
    
    def save(self):
        """Save character and calculate derived stats."""
        self.hit_points = self.calculate_hit_points()
        self.armor_class = self.calculate_armor_class()
        self.initiative = self.calculate_initiative()
        db.session.commit()

# Create indexes for frequently queried fields
Index('idx_character_user_id', Character.user_id)
Index('idx_character_campaign_id', Character.campaign_id)
Index('idx_character_name', Character.name)
