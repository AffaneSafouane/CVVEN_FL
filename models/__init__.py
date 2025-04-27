# Import des modèles pour les rendre disponibles directement depuis le package
from .models import User, Category, Activity, TimeSlot, Reservation, Review

# Import de la fonction d'initialisation de la base de données
from .init_db import main as init_db_main