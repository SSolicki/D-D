from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from datetime import datetime

class CampaignForm(FlaskForm):
    name = StringField('Campaign Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Name must be between 3 and 100 characters')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(max=500, message='Description must be less than 500 characters')
    ])
    setting = StringField('Setting', validators=[
        Optional(),
        Length(max=100, message='Setting must be less than 100 characters')
    ])
    power_level = SelectField('Starting Power Level', choices=[
        ('Novice', 'Novice'),
        ('Seasoned', 'Seasoned'),
        ('Veteran', 'Veteran'),
        ('Heroic', 'Heroic'),
        ('Legendary', 'Legendary')
    ], default='Novice')
    max_players = IntegerField('Maximum Players', validators=[
        DataRequired(),
        NumberRange(min=1, max=10, message='Number of players must be between 1 and 10')
    ], default=6)
    house_rules = TextAreaField('House Rules', validators=[Optional()])
    next_session = DateTimeField('Next Session', format='%Y-%m-%d %H:%M',
                               validators=[Optional()], default=datetime.now)
    submit = SubmitField('Save Campaign')

class CampaignNoteForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Title must be between 3 and 100 characters')
    ])
    content = TextAreaField('Content', validators=[
        DataRequired(),
        Length(min=10, message='Content must be at least 10 characters')
    ])
    note_type = SelectField('Note Type', choices=[
        ('general', 'General'),
        ('quest', 'Quest'),
        ('npc', 'NPC'),
        ('location', 'Location'),
        ('lore', 'Lore')
    ])
    submit = SubmitField('Save Note')

class InviteForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64, message='Username must be between 3 and 64 characters')
    ])
    message = TextAreaField('Message', validators=[Optional()])
    submit = SubmitField('Send Invite')
