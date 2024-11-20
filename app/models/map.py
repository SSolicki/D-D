from app import db
from datetime import datetime
from sqlalchemy import Index

class Map(db.Model):
    __tablename__ = 'map'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    map_type = db.Column(db.String(50), nullable=False)
    grid_width = db.Column(db.Integer, nullable=False)
    grid_height = db.Column(db.Integer, nullable=False)
    background_color = db.Column(db.String(7), nullable=False)
    show_grid = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'map_type': self.map_type,
            'grid_width': self.grid_width,
            'grid_height': self.grid_height,
            'background_color': self.background_color,
            'show_grid': self.show_grid,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'campaign_id': self.campaign_id
        }

# Create indexes for frequently queried fields
Index('idx_map_campaign', Map.campaign_id)
Index('idx_map_creator', Map.created_by)
Index('idx_map_name', Map.name)
