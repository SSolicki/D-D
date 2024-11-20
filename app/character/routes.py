from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.character import bp
from app.models import Character, Campaign
from app.character.forms import CharacterForm

@bp.route('/characters')
@login_required
def list_characters():
    characters = Character.query.filter_by(user_id=current_user.id).all()
    return render_template('character/list.html', characters=characters)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CharacterForm()
    if form.validate_on_submit():
        try:
            character = Character(
                name=form.name.data,
                race=form.race.data,
                character_class=form.character_class.data,
                level=form.level.data,
                background=form.background.data,
                alignment=form.alignment.data,
                strength=str(form.strength.data),
                dexterity=str(form.dexterity.data),
                constitution=str(form.constitution.data),
                intelligence=str(form.intelligence.data),
                wisdom=str(form.wisdom.data),
                charisma=str(form.charisma.data),
                user_id=current_user.id
            )
            db.session.add(character)
            db.session.commit()
            flash('Your character has been created!', 'success')
            return redirect(url_for('character.list_characters'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating character: ' + str(e), 'danger')
            return render_template('character/create.html', form=form)
    
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return render_template('character/create.html', form=form)

@bp.route('/<int:character_id>/join_campaign/<int:campaign_id>')
@login_required
def join_campaign(character_id, campaign_id):
    character = Character.query.get_or_404(character_id)
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Check permissions
    if character.user_id != current_user.id:
        flash('You cannot modify this character.', 'error')
        return redirect(url_for('character.list_characters'))
    
    if campaign.dm_id != current_user.id and current_user not in campaign.players:
        flash('You are not a member of this campaign.', 'error')
        return redirect(url_for('campaign.list_campaigns'))
    
    # Update character's campaign
    character.campaign_id = campaign_id
    db.session.commit()
    flash(f'{character.name} has joined {campaign.name}!', 'success')
    return redirect(url_for('character.view', character_id=character.id))

@bp.route('/<int:character_id>/leave_campaign')
@login_required
def leave_campaign(character_id):
    character = Character.query.get_or_404(character_id)
    
    if character.user_id != current_user.id:
        flash('You cannot modify this character.', 'error')
        return redirect(url_for('character.list_characters'))
    
    if character.campaign_id:
        campaign_name = character.campaign.name
        character.campaign_id = None
        db.session.commit()
        flash(f'{character.name} has left {campaign_name}!', 'success')
    
    return redirect(url_for('character.view', character_id=character.id))

@bp.route('/<int:character_id>')
@login_required
def view(character_id):
    character = Character.query.get_or_404(character_id)
    if character.user_id != current_user.id:
        flash('You cannot view this character.', 'error')
        return redirect(url_for('character.list_characters'))
    
    # Get available campaigns for the character to join
    available_campaigns = Campaign.query.filter(
        (Campaign.dm_id == current_user.id) | 
        (Campaign.players.any(id=current_user.id))
    ).all()
    
    return render_template('character/view.html', 
                         character=character, 
                         available_campaigns=available_campaigns)

@bp.route('/<int:character_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(character_id):
    character = Character.query.get_or_404(character_id)
    if character.user_id != current_user.id:
        flash('You cannot edit this character.', 'error')
        return redirect(url_for('character.list_characters'))
    
    form = CharacterForm(obj=character)
    if form.validate_on_submit():
        character.name = form.name.data
        character.race = form.race.data
        character.character_class = form.character_class.data
        character.level = form.level.data
        character.background = form.background.data
        character.alignment = form.alignment.data
        db.session.commit()
        flash('Your character has been updated!', 'success')
        return redirect(url_for('character.view', character_id=character.id))
    
    return render_template('character/edit.html', form=form, character=character)

@bp.route('/<int:character_id>/delete')
@login_required
def delete(character_id):
    character = Character.query.get_or_404(character_id)
    if character.user_id != current_user.id:
        flash('You cannot delete this character.', 'error')
        return redirect(url_for('character.list_characters'))
    
    db.session.delete(character)
    db.session.commit()
    flash('Your character has been deleted.', 'success')
    return redirect(url_for('character.list_characters'))
