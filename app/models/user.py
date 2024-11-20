from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Index

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    # Relationships
    characters = db.relationship('Character', backref='user', lazy='dynamic')
    owned_campaigns = db.relationship('Campaign', backref='owner', lazy='dynamic',
                                    foreign_keys='Campaign.owner_id')
    created_maps = db.relationship('Map', backref='creator', lazy='dynamic',
                                 foreign_keys='Map.created_by')
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

# Create indexes for frequently queried fields
Index('idx_user_username', User.username)
Index('idx_user_email', User.email)
