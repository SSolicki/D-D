from app import db
from datetime import datetime
from sqlalchemy import Index
import json

# Association table for campaign members
campaign_members = db.Table('campaign_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('campaign_id', db.Integer, db.ForeignKey('campaign.id'), primary_key=True)
)

class Campaign(db.Model):
    __tablename__ = 'campaign'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    setting = db.Column(db.String(100))
    
    # Campaign Rules
    power_level = db.Column(db.String(50), default='Novice')
    available_races = db.Column(db.String(1000))
    available_edges = db.Column(db.String(1000))
    house_rules = db.Column(db.Text)
    
    # Campaign Status
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    next_session = db.Column(db.DateTime)
    
    # Relationships
    characters = db.relationship('Character', lazy='dynamic')
    notes = db.relationship('CampaignNote', backref='campaign', lazy='dynamic',
                          cascade='all, delete-orphan')
    maps = db.relationship('Map', backref='campaign', lazy='dynamic',
                         cascade='all, delete-orphan')
    members = db.relationship('User', secondary=campaign_members,
                            lazy='dynamic',
                            backref=db.backref('campaigns', lazy='dynamic'))
    
    def get_available_races(self):
        return json.loads(self.available_races) if self.available_races else []
    
    def set_available_races(self, races):
        self.available_races = json.dumps(races)
    
    def get_available_edges(self):
        return json.loads(self.available_edges) if self.available_edges else []
    
    def set_available_edges(self, edges):
        self.available_edges = json.dumps(edges)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'setting': self.setting,
            'power_level': self.power_level,
            'status': self.status,
            'next_session': self.next_session.isoformat() if self.next_session else None,
            'owner': self.owner.to_dict() if self.owner else None
        }

# Create indexes for frequently queried fields
Index('idx_campaign_owner_id', Campaign.owner_id)
Index('idx_campaign_name', Campaign.name)
Index('idx_campaign_status', Campaign.status)
