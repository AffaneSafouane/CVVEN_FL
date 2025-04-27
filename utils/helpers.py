import os
import uuid
from flask import current_app, flash, redirect, url_for
from werkzeug.utils import secure_filename
from flask_login import current_user
from functools import wraps

def save_image(image_file):
    """
    Sauvegarde une image téléchargée avec un nom de fichier unique
    
    Args:
        image_file: Fichier d'image téléchargé via un formulaire
        
    Returns:
        str: Nom du fichier sauvegardé ou None en cas d'erreur
    """
    # Vérifier si le répertoire d'upload existe, sinon le créer
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Générer un nom de fichier unique
    filename = secure_filename(image_file.filename)
    _, ext = os.path.splitext(filename)
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    
    # Sauvegarder l'image
    try:
        image_file.save(os.path.join(upload_folder, unique_filename))
        return unique_filename
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la sauvegarde de l'image: {str(e)}")
        return None

def get_image_url(filename):
    """
    Obtient l'URL d'une image à partir de son nom de fichier
    
    Args:
        filename: Nom du fichier image
        
    Returns:
        str: URL de l'image ou URL d'une image par défaut
    """
    if not filename:
        return url_for('static', filename='images/default-activity.jpg')
    
    # Vérifier si le fichier existe
    if os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)):
        return url_for('static', filename=f'uploads/{filename}')
    else:
        return url_for('static', filename='images/default-activity.jpg')

def admin_required(f):
    """
    Décorateur pour restreindre l'accès aux administrateurs seulement
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Accès refusé. Vous devez être administrateur pour accéder à cette page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def format_duration(minutes):
    """
    Formate une durée en minutes en format lisible
    
    Args:
        minutes: Durée en minutes
        
    Returns:
        str: Durée formatée (ex: "1h 30min")
    """
    if minutes < 60:
        return f"{minutes}min"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if remaining_minutes == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {remaining_minutes}min"

def format_price(price):
    """
    Formate un prix avec deux décimales et symbole €
    
    Args:
        price: Prix à formater
        
    Returns:
        str: Prix formaté (ex: "15,00 €")
    """
    if price is None:
        return "0,00 €"
    
    return f"{float(price):.2f} €".replace('.', ',')
