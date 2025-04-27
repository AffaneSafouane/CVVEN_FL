from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    name = StringField('Nom complet', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Adresse email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(),
        Length(min=8, message='Le mot de passe doit contenir au moins 8 caractères')
    ])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        EqualTo('password', message='Les mots de passe doivent correspondre')
    ])
    submit = SubmitField('S\'inscrire')
    
    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user:
            raise ValidationError('Cette adresse email est déjà utilisée. Veuillez en choisir une autre.')

class LoginForm(FlaskForm):
    email = StringField('Adresse email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class ProfileUpdateForm(FlaskForm):
    name = StringField('Nom complet', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Adresse email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Mot de passe actuel')
    new_password = PasswordField('Nouveau mot de passe', 
                              validators=[Length(min=8, message='Le mot de passe doit contenir au moins 8 caractères')])
    confirm_password = PasswordField('Confirmer le nouveau mot de passe', 
                                 validators=[EqualTo('new_password', message='Les mots de passe doivent correspondre')])
    submit = SubmitField('Mettre à jour')
    
    def __init__(self, current_user, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.current_user = current_user
        
    def validate_email(self, email):
        if email.data != self.current_user.email:
            user = User.objects(email=email.data).first()
            if user:
                raise ValidationError('Cette adresse email est déjà utilisée. Veuillez en choisir une autre.')
    
    def validate_current_password(self, current_password):
        if self.new_password.data and not self.current_user.check_password(current_password.data):
            raise ValidationError('Mot de passe incorrect.')
