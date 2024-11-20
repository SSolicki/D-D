from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db, cache
from app.campaign import bp
from app.campaign.forms import CampaignForm, CampaignNoteForm, InviteForm
from app.models import Campaign, CampaignNote, User, Character
from app.errors.handlers import CampaignError
from sqlalchemy.exc import IntegrityError
from datetime import datetime

@bp.route('/')
@login_required
def index():
    """Show all campaigns with filtering based on user's role."""
    # Get all campaigns the user is involved with
    campaigns = Campaign.query.all()
    user_campaigns = [c.id for c in current_user.campaigns]
    
    return render_template('campaign/index.html', 
                         campaigns=campaigns,
                         user_campaigns=user_campaigns)

@bp.route('/create', methods=['POST'])
@login_required
def create():
    """Create a new campaign."""
    form = CampaignForm()
    if form.validate_on_submit():
        try:
            campaign = Campaign(
                name=form.name.data,
                description=form.description.data,
                setting=form.setting.data,
                power_level=form.power_level.data,
                max_players=form.max_players.data,
                owner=current_user,
                status='active'
            )
            campaign.members.append(current_user)  # Owner is also a member
            db.session.add(campaign)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Campaign created successfully'})
        except IntegrityError:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'A campaign with that name already exists'})
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating campaign: {str(e)}')
            return jsonify({'success': False, 'message': 'An error occurred while creating the campaign'})
    return jsonify({'success': False, 'message': 'Invalid form data'})

@bp.route('/<int:campaign_id>')
@login_required
def view(campaign_id):
    """View a specific campaign."""
    campaign = Campaign.query.get_or_404(campaign_id)
    if current_user not in campaign.members and current_user != campaign.owner:
        flash('You do not have access to this campaign.', 'danger')
        return redirect(url_for('campaign.index'))
    
    note_form = CampaignNoteForm()
    invite_form = InviteForm()
    return render_template('campaign/details.html', 
                         campaign=campaign,
                         note_form=note_form,
                         invite_form=invite_form)

@bp.route('/<int:campaign_id>/join', methods=['POST'])
@login_required
def join(campaign_id):
    """Join a campaign."""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if current_user in campaign.members:
        return jsonify({'success': False, 'message': 'You are already a member of this campaign'})
    
    if len(campaign.members) >= campaign.max_players:
        return jsonify({'success': False, 'message': 'This campaign is full'})
    
    try:
        campaign.members.append(current_user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Successfully joined the campaign'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error joining campaign: {str(e)}')
        return jsonify({'success': False, 'message': 'An error occurred while joining the campaign'})

@bp.route('/<int:campaign_id>/leave', methods=['POST'])
@login_required
def leave(campaign_id):
    """Leave a campaign."""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if current_user == campaign.owner:
        return jsonify({'success': False, 'message': 'The campaign owner cannot leave the campaign'})
    
    if current_user not in campaign.members:
        return jsonify({'success': False, 'message': 'You are not a member of this campaign'})
    
    try:
        campaign.members.remove(current_user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Successfully left the campaign'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error leaving campaign: {str(e)}')
        return jsonify({'success': False, 'message': 'An error occurred while leaving the campaign'})

@bp.route('/<int:campaign_id>/edit', methods=['POST'])
@login_required
def edit(campaign_id):
    """Edit campaign details."""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if current_user != campaign.owner:
        return jsonify({'success': False, 'message': 'Only the campaign owner can edit campaign details'})
    
    form = CampaignForm()
    if form.validate_on_submit():
        try:
            campaign.name = form.name.data
            campaign.description = form.description.data
            campaign.setting = form.setting.data
            campaign.power_level = form.power_level.data
            campaign.max_players = form.max_players.data
            db.session.commit()
            return jsonify({'success': True, 'message': 'Campaign updated successfully'})
        except IntegrityError:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'A campaign with that name already exists'})
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating campaign: {str(e)}')
            return jsonify({'success': False, 'message': 'An error occurred while updating the campaign'})
    return jsonify({'success': False, 'message': 'Invalid form data'})

@bp.route('/<int:campaign_id>/invite', methods=['POST'])
@login_required
def invite(campaign_id):
    """Invite a player to the campaign."""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if current_user != campaign.owner:
        return jsonify({'success': False, 'message': 'Only the campaign owner can invite players'})
    
    form = InviteForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})
        
        if user in campaign.members:
            return jsonify({'success': False, 'message': 'User is already a member of this campaign'})
        
        if len(campaign.members) >= campaign.max_players:
            return jsonify({'success': False, 'message': 'Campaign is full'})
        
        try:
            campaign.members.append(user)
            db.session.commit()
            return jsonify({'success': True, 'message': f'Successfully invited {user.username} to the campaign'})
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error inviting player: {str(e)}')
            return jsonify({'success': False, 'message': 'An error occurred while inviting the player'})
    return jsonify({'success': False, 'message': 'Invalid form data'})

@bp.route('/<int:campaign_id>/note', methods=['POST'])
@login_required
def add_note(campaign_id):
    """Add a note to the campaign."""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if current_user not in campaign.members:
        return jsonify({'success': False, 'message': 'Only campaign members can add notes'})
    
    form = CampaignNoteForm()
    if form.validate_on_submit():
        try:
            note = CampaignNote(
                campaign_id=campaign_id,
                author=current_user,
                title=form.title.data,
                content=form.content.data,
                note_type=form.note_type.data
            )
            db.session.add(note)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Note added successfully'})
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error adding note: {str(e)}')
            return jsonify({'success': False, 'message': 'An error occurred while adding the note'})
    return jsonify({'success': False, 'message': 'Invalid form data'})
