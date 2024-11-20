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
    character_class = StringField('Class', validators=[
        DataRequired(),
        Length(max=50, message='Class must be less than 50 characters')
    ])
    level = IntegerField('Level', validators=[
        DataRequired(),
        NumberRange(min=1, max=20, message='Level must be between 1 and 20')
    ], default=1)
    background = StringField('Background', validators=[
        Optional(),
        Length(max=100, message='Background must be less than 100 characters')
    ])
    alignment = SelectField('Alignment', choices=[
        ('LG', 'Lawful Good'),
        ('NG', 'Neutral Good'),
        ('CG', 'Chaotic Good'),
        ('LN', 'Lawful Neutral'),
        ('N', 'True Neutral'),
        ('CN', 'Chaotic Neutral'),
        ('LE', 'Lawful Evil'),
        ('NE', 'Neutral Evil'),
        ('CE', 'Chaotic Evil')
    ])
    
    # Ability Scores
    strength = IntegerField('Strength', validators=[
        DataRequired(),
        NumberRange(min=3, max=20, message='Strength must be between 3 and 20')
    ], default=10)
    dexterity = IntegerField('Dexterity', validators=[
        DataRequired(),
        NumberRange(min=3, max=20, message='Dexterity must be between 3 and 20')
    ], default=10)
    constitution = IntegerField('Constitution', validators=[
        DataRequired(),
        NumberRange(min=3, max=20, message='Constitution must be between 3 and 20')
    ], default=10)
    intelligence = IntegerField('Intelligence', validators=[
        DataRequired(),
        NumberRange(min=3, max=20, message='Intelligence must be between 3 and 20')
    ], default=10)
    wisdom = IntegerField('Wisdom', validators=[
        DataRequired(),
        NumberRange(min=3, max=20, message='Wisdom must be between 3 and 20')
    ], default=10)
    charisma = IntegerField('Charisma', validators=[
        DataRequired(),
        NumberRange(min=3, max=20, message='Charisma must be between 3 and 20')
    ], default=10)
    
    # Equipment
    equipment = TextAreaField('Equipment', validators=[Optional()])
    gold = IntegerField('Gold Pieces', validators=[Optional(), NumberRange(min=0)], default=0)
    
    # Character Details
    personality = TextAreaField('Personality Traits', validators=[Optional()])
    ideals = TextAreaField('Ideals', validators=[Optional()])
    bonds = TextAreaField('Bonds', validators=[Optional()])
    flaws = TextAreaField('Flaws', validators=[Optional()])
    backstory = TextAreaField('Backstory', validators=[Optional()])
    
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
