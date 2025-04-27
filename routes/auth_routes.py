from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from forms.auth_forms import RegistrationForm, LoginForm, ProfileUpdateForm
from models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        user.save()
        
        flash('Votre compte a été créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', title='Inscription', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Connexion réussie!', 'success')
            return redirect(next_page if next_page else url_for('index'))
        else:
            flash('Échec de la connexion. Veuillez vérifier votre email et votre mot de passe.', 'danger')
            
    return render_template('auth/login.html', title='Connexion', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileUpdateForm(current_user)
    
    if request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        
        if form.new_password.data:
            current_user.set_password(form.new_password.data)
            
        current_user.save()
        flash('Votre profil a été mis à jour avec succès!', 'success')
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/profile.html', title='Mon Profil', form=form)
