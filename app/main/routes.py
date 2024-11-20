from flask import render_template, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import cache, limiter
from app.main import bp
from app.models import Campaign, Character
import logging

@bp.route('/')
@bp.route('/index')
@cache.cached(timeout=60)
def index():
    """Home page with recent activity and statistics."""
    try:
        if current_user.is_authenticated:
            # Get counts for user stats
            user_stats = {
                'character_count': Character.query.filter_by(user_id=current_user.id).count(),
                'campaign_count': Campaign.query.filter(Campaign.members.any(id=current_user.id)).count(),
                'dm_campaign_count': Campaign.query.filter_by(owner_id=current_user.id).count()
            }

            recent_campaigns = Campaign.query.filter(
                Campaign.members.any(id=current_user.id)
            ).order_by(Campaign.created_at.desc()).limit(5).all()
            
            recent_characters = Character.query.filter_by(
                user_id=current_user.id
            ).order_by(Character.created_at.desc()).limit(5).all()
        else:
            recent_campaigns = []
            recent_characters = []
            user_stats = {
                'character_count': 0,
                'campaign_count': 0,
                'dm_campaign_count': 0
            }
            
        stats = {
            'total_campaigns': Campaign.query.count(),
            'total_characters': Character.query.count()
        }
        
        return render_template('main/index.html',
                             recent_campaigns=recent_campaigns,
                             recent_characters=recent_characters,
                             user_stats=user_stats,
                             stats=stats,
                             error=False)
                             
    except Exception as e:
        logging.error(f'Error in index route: {str(e)}')
        # Pass empty user_stats when there's an error
        return render_template('main/index.html', 
                             error=True,
                             user_stats={'character_count': 0, 'campaign_count': 0, 'dm_campaign_count': 0})

@bp.route('/dashboard')
@login_required
@cache.cached(timeout=30)
def dashboard():
    """User dashboard with their campaigns and characters."""
    try:
        user_campaigns = current_user.campaigns.all()
        user_characters = current_user.characters.all()
        owned_campaigns = current_user.owned_campaigns.all()
        
        campaign_stats = {
            'total': len(user_campaigns),
            'owned': len(owned_campaigns),
            'participating': len(user_campaigns) - len(owned_campaigns)
        }
        
        character_stats = {
            'total': len(user_characters),
            'in_campaign': sum(1 for c in user_characters if c.campaign_id is not None),
            'available': sum(1 for c in user_characters if c.campaign_id is None)
        }
        
        return render_template('main/dashboard.html',
                             campaigns=user_campaigns,
                             characters=user_characters,
                             campaign_stats=campaign_stats,
                             character_stats=character_stats)
                             
    except Exception as e:
        logging.error(f'Error in dashboard route: {str(e)}')
        return redirect(url_for('main.index'))

@bp.route('/about')
def about():
    """About page with application information."""
    return render_template('main/about.html')

@bp.route('/help')
def help():
    """Help page with documentation and guides."""
    return render_template('main/help.html')
