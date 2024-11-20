from app import db
from app.models import User, Character, Campaign, Item, Map, CampaignNote

def init_db():
    """Initialize the database."""
    # Import all models to ensure they are registered with SQLAlchemy
    from app.models import (
        User,
        Character,
        Campaign,
        campaign_members,
        Item,
        CharacterInventory,
        Map,
        CampaignNote
    )
    
    # Create all tables
    db.create_all()

def reset_db():
    """Reset the database (for development only)."""
    db.drop_all()
    db.create_all()
