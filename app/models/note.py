from app import db
from datetime import datetime
from sqlalchemy import Index

class CampaignNote(db.Model):
    __tablename__ = 'campaign_note'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    note_type = db.Column(db.String(50))  # e.g., 'session_summary', 'plot_hook', 'npc_note'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    author = db.relationship('User', foreign_keys=[created_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'title': self.title,
            'content': self.content,
            'note_type': self.note_type,
            'created_at': self.created_at.isoformat(),
            'author': self.author.username
        }

# Create indexes for frequently queried fields
Index('idx_note_campaign', CampaignNote.campaign_id)
Index('idx_note_author', CampaignNote.created_by)
Index('idx_note_type', CampaignNote.note_type)
