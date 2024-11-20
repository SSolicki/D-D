from app import db
from sqlalchemy import Index

class Item(db.Model):
    __tablename__ = 'item'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, default=0)
    item_type = db.Column(db.String(50), nullable=False)
    
    # Combat Stats
    damage = db.Column(db.String(20))
    range = db.Column(db.String(20))
    ap = db.Column(db.Integer)
    rof = db.Column(db.Integer, default=1)
    shots = db.Column(db.Integer)
    min_str = db.Column(db.String(10))
    
    # Armor Stats
    armor = db.Column(db.Integer)
    coverage = db.Column(db.String(50))
    
    # General Stats
    cost = db.Column(db.Integer)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'weight': self.weight,
            'item_type': self.item_type,
            'damage': self.damage,
            'range': self.range,
            'ap': self.ap,
            'rof': self.rof,
            'shots': self.shots,
            'min_str': self.min_str,
            'armor': self.armor,
            'coverage': self.coverage,
            'cost': self.cost,
            'notes': self.notes
        }

class CharacterInventory(db.Model):
    __tablename__ = 'character_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    equipped = db.Column(db.Boolean, default=False)
    
    # Relationship
    item = db.relationship('Item')
    
    def to_dict(self):
        item_dict = self.item.to_dict()
        return {
            'id': self.id,
            'character_id': self.character_id,
            'item': item_dict,
            'quantity': self.quantity,
            'equipped': self.equipped
        }

# Create indexes for frequently queried fields
Index('idx_item_name', Item.name)
Index('idx_item_type', Item.item_type)
Index('idx_inventory_character', CharacterInventory.character_id)
Index('idx_inventory_item', CharacterInventory.item_id)
Index('idx_inventory_equipped', CharacterInventory.equipped)
