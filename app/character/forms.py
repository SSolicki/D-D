from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class CharacterForm(FlaskForm):
    name = StringField('Character Name', validators=[
        DataRequired(),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    race = StringField('Race', validators=[
        DataRequired(),
        Length(max=50, message='Race must be less than 50 characters')
    ])
    
    # In Savage Worlds, we don't have classes but archetypes/concepts
    character_concept = StringField('Character Concept', validators=[
        DataRequired(),
        Length(max=100, message='Concept must be less than 100 characters')
    ])
    
    # Savage Worlds uses ranks instead of levels
    rank = SelectField('Rank', choices=[
        ('Novice', 'Novice'),
        ('Seasoned', 'Seasoned'),
        ('Veteran', 'Veteran'),
        ('Heroic', 'Heroic'),
        ('Legendary', 'Legendary')
    ], validators=[DataRequired()])
    
    # Attributes in Savage Worlds use die types
    agility = SelectField('Agility', choices=[
        ('d4', 'd4'),
        ('d6', 'd6'),
        ('d8', 'd8'),
        ('d10', 'd10'),
        ('d12', 'd12')
    ], validators=[DataRequired()])
    
    smarts = SelectField('Smarts', choices=[
        ('d4', 'd4'),
        ('d6', 'd6'),
        ('d8', 'd8'),
        ('d10', 'd10'),
        ('d12', 'd12')
    ], validators=[DataRequired()])
    
    spirit = SelectField('Spirit', choices=[
        ('d4', 'd4'),
        ('d6', 'd6'),
        ('d8', 'd8'),
        ('d10', 'd10'),
        ('d12', 'd12')
    ], validators=[DataRequired()])
    
    strength = SelectField('Strength', choices=[
        ('d4', 'd4'),
        ('d6', 'd6'),
        ('d8', 'd8'),
        ('d10', 'd10'),
        ('d12', 'd12')
    ], validators=[DataRequired()])
    
    vigor = SelectField('Vigor', choices=[
        ('d4', 'd4'),
        ('d6', 'd6'),
        ('d8', 'd8'),
        ('d10', 'd10'),
        ('d12', 'd12')
    ], validators=[DataRequired()])
    
    # Character Details
    hindrances = TextAreaField('Hindrances', validators=[Optional()])
    edges = TextAreaField('Edges', validators=[Optional()])
    equipment = TextAreaField('Equipment', validators=[Optional()])
    
    # Money in Savage Worlds
    money = IntegerField('Money', validators=[Optional(), NumberRange(min=0)], default=500)
    
    # Additional Character Details
    background = TextAreaField('Background', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    
    submit = SubmitField('Create Character')


class LevelUpForm(FlaskForm):
    new_level = IntegerField('New Level', validators=[
        DataRequired(),
        NumberRange(min=2, max=20, message='Level must be between 2 and 20')
    ])
    hp_increase = IntegerField('HP Increase', validators=[
        DataRequired(),
        NumberRange(min=1, message='HP increase must be at least 1')
    ])
    notes = TextAreaField('Level Up Notes', validators=[Optional()])
    submit = SubmitField('Level Up')
