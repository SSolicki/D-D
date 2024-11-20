from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db, cache
from app.inventory import bp
from app.models import Character, Item, CharacterInventory, Campaign
import logging
from sqlalchemy.exc import IntegrityError

@bp.route('/inventory/<int:character_id>')
@login_required
@cache.cached(timeout=30)
def view_inventory(character_id):
    """View a character's inventory."""
    character = Character.query.get_or_404(character_id)
    campaign = Campaign.query.get_or_404(character.campaign_id)
    
    if not campaign.is_member(current_user):
        flash('You do not have access to this inventory.', 'error')
        return redirect(url_for('main.index'))
    
    inventory = CharacterInventory.query.filter_by(character_id=character_id).all()
    return render_template('inventory/view.html',
                         character=character,
                         inventory=inventory,
                         is_owner=character.user_id == current_user.id)

@bp.route('/inventory/<int:character_id>/add', methods=['GET', 'POST'])
@login_required
def add_item(character_id):
    """Add an item to character's inventory."""
    character = Character.query.get_or_404(character_id)
    
    if character.user_id != current_user.id:
        flash('You can only modify your own character\'s inventory.', 'error')
        return redirect(url_for('inventory.view_inventory', character_id=character_id))
    
    if request.method == 'POST':
        item_id = request.form.get('item_id')
        quantity = int(request.form.get('quantity', 1))
        
        try:
            item = Item.query.get_or_404(item_id)
            inventory_item = CharacterInventory(
                character_id=character_id,
                item_id=item_id,
                quantity=quantity
            )
            
            db.session.add(inventory_item)
            db.session.commit()
            
            flash(f'Added {quantity} {item.name}(s) to inventory.', 'success')
            return redirect(url_for('inventory.view_inventory', character_id=character_id))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f'Error adding item to inventory: {str(e)}')
            flash('Error adding item to inventory. Please try again.', 'error')
    
    items = Item.query.all()
    return render_template('inventory/add_item.html',
                         character=character,
                         items=items)

@bp.route('/inventory/<int:character_id>/remove/<int:inventory_id>')
@login_required
def remove_item(character_id, inventory_id):
    """Remove an item from character's inventory."""
    character = Character.query.get_or_404(character_id)
    inventory_item = CharacterInventory.query.get_or_404(inventory_id)
    
    if character.user_id != current_user.id:
        flash('You can only modify your own character\'s inventory.', 'error')
        return redirect(url_for('inventory.view_inventory', character_id=character_id))
    
    if inventory_item.character_id != character_id:
        flash('Invalid inventory item.', 'error')
        return redirect(url_for('inventory.view_inventory', character_id=character_id))
    
    try:
        db.session.delete(inventory_item)
        db.session.commit()
        flash('Item removed from inventory.', 'success')
        
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error removing item from inventory: {str(e)}')
        flash('Error removing item from inventory. Please try again.', 'error')
    
    return redirect(url_for('inventory.view_inventory', character_id=character_id))

@bp.route('/inventory/<int:character_id>/toggle/<int:inventory_id>')
@login_required
def toggle_equipped(character_id, inventory_id):
    """Toggle whether an item is equipped."""
    character = Character.query.get_or_404(character_id)
    inventory_item = CharacterInventory.query.get_or_404(inventory_id)
    
    if character.user_id != current_user.id:
        flash('You can only modify your own character\'s inventory.', 'error')
        return redirect(url_for('inventory.view_inventory', character_id=character_id))
    
    if inventory_item.character_id != character_id:
        flash('Invalid inventory item.', 'error')
        return redirect(url_for('inventory.view_inventory', character_id=character_id))
    
    try:
        inventory_item.equipped = not inventory_item.equipped
        db.session.commit()
        status = 'equipped' if inventory_item.equipped else 'unequipped'
        flash(f'Item {status}.', 'success')
        
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error toggling item equipped status: {str(e)}')
        flash('Error updating item status. Please try again.', 'error')
    
    return redirect(url_for('inventory.view_inventory', character_id=character_id))

@bp.route('/api/inventory/<int:character_id>')
@login_required
def get_inventory(character_id):
    """API endpoint to get character's inventory."""
    character = Character.query.get_or_404(character_id)
    campaign = Campaign.query.get_or_404(character.campaign_id)
    
    if not campaign.is_member(current_user):
        return jsonify({'error': 'Access denied'}), 403
    
    inventory = CharacterInventory.query.filter_by(character_id=character_id).all()
    inventory_data = []
    
    for item in inventory:
        inventory_data.append({
            'id': item.id,
            'item_id': item.item_id,
            'name': item.item.name,
            'quantity': item.quantity,
            'equipped': item.equipped,
            'weight': item.item.weight,
            'type': item.item.item_type,
            'damage': item.item.damage,
            'range': item.item.range,
            'notes': item.item.notes
        })
    
    return jsonify(inventory_data)
