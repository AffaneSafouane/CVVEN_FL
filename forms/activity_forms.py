from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from models import Category

class ActivityCreationForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    price = DecimalField('Prix', validators=[DataRequired(), NumberRange(min=0)])
    duration = IntegerField('Durée (minutes)', validators=[DataRequired(), NumberRange(min=5)])
    location = StringField('Lieu', validators=[DataRequired()])
    category_id = SelectField('Catégorie', coerce=str)
    max_participants = IntegerField('Nombre maximum de participants', 
                                validators=[DataRequired(), NumberRange(min=1)])
    image = FileField('Image de l\'activité', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images seulement!')
    ])
    submit = SubmitField('Créer l\'activité')
    
    def __init__(self, *args, **kwargs):
        super(ActivityCreationForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(str(c.id), c.name) for c in Category.objects.all()]
        # Ajout d'une option vide si nécessaire
        self.category_id.choices.insert(0, ('', 'Sélectionnez une catégorie'))

class ActivityUpdateForm(ActivityCreationForm):
    submit = SubmitField('Mettre à jour l\'activité')

class ReviewForm(FlaskForm):
    rating = SelectField('Note', choices=[(str(i), f'{i} étoiles') for i in range(1, 6)], 
                      validators=[DataRequired()], coerce=int)
    comment = TextAreaField('Commentaire', validators=[Length(max=500)])
    submit = SubmitField('Soumettre')

class ActivitySearchForm(FlaskForm):
    search_query = StringField('Rechercher', validators=[Length(max=100)])
    category = SelectField('Catégorie', coerce=str)
    min_price = DecimalField('Prix minimum', validators=[NumberRange(min=0)], default=0)
    max_price = DecimalField('Prix maximum', validators=[NumberRange(min=0)])
    location = StringField('Lieu', validators=[Length(max=100)])
    submit = SubmitField('Rechercher')
    
    def __init__(self, *args, **kwargs):
        super(ActivitySearchForm, self).__init__(*args, **kwargs)
        self.category.choices = [(str(c.id), c.name) for c in Category.objects.all()]
        # Ajout d'une option "Toutes les catégories"
        self.category.choices.insert(0, ('', 'Toutes les catégories'))
