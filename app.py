from flask import Flask, render_template
from config import Config
from mongoengine import connect
from flask_login import LoginManager
from datetime import datetime, timezone

app = Flask(__name__)
app.config.from_object(Config)

# Connect to MongoDB
connect(host=app.config['MONGODB_URI'])

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Import des modèles après l'initialisation de l'app pour éviter les imports circulaires
from models import User
from routes import auth_bp, activity_bp, reservation_bp, admin_bp

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(activity_bp)
app.register_blueprint(reservation_bp)
app.register_blueprint(admin_bp)

# Commande CLI pour initialiser la base de données
@app.cli.command('initdb')
def initdb():
    """Initialisation de la base de données avec des données de test"""
    from models import init_db_main
    init_db_main()

@app.context_processor
def inject_now():
    return {'now': datetime.now(timezone.utc)}

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)