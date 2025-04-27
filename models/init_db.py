#!/usr/bin/env python3
"""
Script d'initialisation de la base de données avec des données de démo.
Crée un utilisateur admin, des catégories, des activités et des créneaux horaires.
"""

import os
import sys
from datetime import datetime, timedelta
from mongoengine import connect
from werkzeug.security import generate_password_hash
import random

# Ajouter le répertoire courant au PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importer la configuration et les modèles
from config import Config
from models import User, Category, Activity, TimeSlot

def connect_to_db():
    """Se connecter à la base de données MongoDB"""
    print("Connexion à la base de données...")
    connect(host=Config.MONGODB_URI)
    print(f"Connecté à {Config.MONGODB_URI}")

def create_admin_user():
    """Supprimer les users"""
    print("Suppression des users...")
    User.objects.all().delete()

    """Créer un utilisateur administrateur par défaut"""
    print("Création de l'utilisateur administrateur...")
    
    # Vérifier si l'utilisateur admin existe déjà
    admin = User.objects(email="admin@example.com").first()
    if admin:
        print("L'utilisateur administrateur existe déjà.")
        return admin
    
    # Créer l'utilisateur admin
    admin = User(
        email="admin@example.com",
        name="Administrateur",
        role="admin",
        password_hash=generate_password_hash("admin123")
    )
    admin.save()
    print("Utilisateur administrateur créé avec succès.")
    return admin

def create_test_user():
    """Créer un utilisateur de test"""
    print("Création d'un utilisateur de test...")
    
    # Vérifier si l'utilisateur de test existe déjà
    test_user = User.objects(email="user@example.com").first()
    if test_user:
        print("L'utilisateur de test existe déjà.")
        return test_user
    
    # Créer l'utilisateur de test
    test_user = User(
        email="user@example.com",
        name="Utilisateur Test",
        role="user",
        password_hash=generate_password_hash("user123")
    )
    test_user.save()
    print("Utilisateur de test créé avec succès.")
    return test_user

def create_categories():
    """Supprimer les categories"""
    print("Suppression des categories...")
    Category.objects.all().delete()

    """Créer des catégories d'activités"""
    print("Création des catégories...")
    
    categories_data = [
        {
            "name": "Sports nautiques",
            "description": "Activités aquatiques et nautiques : plongée, kayak, voile, etc."
        },
        {
            "name": "Randonnée",
            "description": "Explorez la nature avec nos randonnées guidées."
        },
        {
            "name": "Gastronomie",
            "description": "Dégustations, cours de cuisine et découvertes culinaires."
        },
        {
            "name": "Bien-être",
            "description": "Yoga, spa, massages et autres activités de relaxation."
        },
        {
            "name": "Culture",
            "description": "Visites guidées, musées, expositions et ateliers culturels."
        },
        {
            "name": "Aventure",
            "description": "Activités à sensations fortes : escalade, parachutisme, rafting, etc."
        }
    ]
    
    created_categories = []
    
    for cat_data in categories_data:
        # Vérifier si la catégorie existe déjà
        existing_category = Category.objects(name=cat_data["name"]).first()
        if existing_category:
            print(f"La catégorie '{cat_data['name']}' existe déjà.")
            created_categories.append(existing_category)
            continue
        
        # Créer la nouvelle catégorie
        category = Category(
            name=cat_data["name"],
            description=cat_data["description"]
        )
        category.save()
        created_categories.append(category)
        print(f"Catégorie '{cat_data['name']}' créée avec succès.")
    
    return created_categories

def create_activities(categories):
    """Supprimer les activités"""
    print("Suppression des activités...")
    Activity.objects.all().delete()
    """Créer des activités exemples pour chaque catégorie"""
    print("Création des activités...")
    
    activities_data = [
        # Sports nautiques
        {
            "title": "Plongée sous-marine",
            "description": "Découvrez la vie marine lors d'une plongée guidée. Équipement fourni et instructeurs certifiés. Adapté aux débutants comme aux plongeurs expérimentés.",
            "price": 85.00,
            "duration": 180,  # 3 heures
            "location": "Plage des Coraux",
            "category_name": "Sports nautiques",
            "max_participants": 8
        },
        {
            "title": "Kayak en mer",
            "description": "Pagayez le long de la côte et explorez des criques inaccessibles. Kayaks simples et doubles disponibles. Inclut une pause baignade et snorkeling.",
            "price": 45.00,
            "duration": 240,  # 4 heures
            "location": "Port des Sables",
            "category_name": "Sports nautiques",
            "max_participants": 12
        },
        
        # Randonnée
        {
            "title": "Randonnée en montagne",
            "description": "Parcourez les sentiers de montagne avec un guide expérimenté. Vue panoramique garantie. Niveau modéré, prévoir des chaussures adaptées.",
            "price": 30.00,
            "duration": 300,  # 5 heures
            "location": "Mont Ventoux",
            "category_name": "Randonnée",
            "max_participants": 15
        },
        {
            "title": "Balade nocturne",
            "description": "Découvrez la forêt sous un autre jour lors d'une randonnée nocturne. Observation des étoiles et de la faune nocturne. Lampes frontales fournies.",
            "price": 25.00,
            "duration": 120,  # 2 heures
            "location": "Forêt des Cèdres",
            "category_name": "Randonnée",
            "max_participants": 10
        },
        
        # Gastronomie
        {
            "title": "Cours de cuisine provençale",
            "description": "Apprenez à préparer les plats emblématiques de la cuisine provençale avec un chef local. Dégustation des plats préparés incluse.",
            "price": 65.00,
            "duration": 180,  # 3 heures
            "location": "Atelier Culinaire Central",
            "category_name": "Gastronomie",
            "max_participants": 8
        },
        {
            "title": "Dégustation de vins",
            "description": "Visite d'un vignoble local suivie d'une dégustation commentée de différents cépages. Planche de fromages et charcuterie incluse.",
            "price": 40.00,
            "duration": 120,  # 2 heures
            "location": "Domaine Viticole Saint-Pierre",
            "category_name": "Gastronomie",
            "max_participants": 12
        },
        
        # Bien-être
        {
            "title": "Yoga au lever du soleil",
            "description": "Session de yoga en plein air face à la mer au lever du soleil. Tous niveaux bienvenus. Tapis de yoga fournis.",
            "price": 20.00,
            "duration": 90,  # 1h30
            "location": "Plage du Levant",
            "category_name": "Bien-être",
            "max_participants": 15
        },
        {
            "title": "Initiation à la méditation",
            "description": "Apprenez les techniques de base de la méditation dans un cadre paisible. Session guidée suivie d'une pratique libre.",
            "price": 25.00,
            "duration": 120,  # 2 heures
            "location": "Jardin Zen",
            "category_name": "Bien-être",
            "max_participants": 10
        },
        
        # Culture
        {
            "title": "Visite guidée du centre historique",
            "description": "Découvrez l'histoire et l'architecture du centre-ville avec un guide passionné. Points d'intérêt : cathédrale, places historiques, ruelles médiévales.",
            "price": 15.00,
            "duration": 120,  # 2 heures
            "location": "Office de Tourisme",
            "category_name": "Culture",
            "max_participants": 20
        },
        {
            "title": "Atelier poterie traditionnelle",
            "description": "Initiez-vous à la poterie traditionnelle et repartez avec votre création. Tous les matériaux sont fournis.",
            "price": 35.00,
            "duration": 150,  # 2h30
            "location": "Atelier des Artisans",
            "category_name": "Culture",
            "max_participants": 8
        },
        
        # Aventure
        {
            "title": "Escalade en falaise",
            "description": "Grimpez des voies adaptées à votre niveau avec un moniteur diplômé. Équipement complet fourni et briefing sécurité inclus.",
            "price": 50.00,
            "duration": 240,  # 4 heures
            "location": "Falaises du Lion",
            "category_name": "Aventure",
            "max_participants": 6
        },
        {
            "title": "Parapente biplace",
            "description": "Envolez-vous en parapente biplace avec un pilote expérimenté. Vue imprenable garantie. Vol de 15-20 minutes selon conditions météo.",
            "price": 90.00,
            "duration": 60,  # 1 heure (préparation + vol)
            "location": "Col des Aigles",
            "category_name": "Aventure",
            "max_participants": 1  # Vol individuel
        }
    ]
    
    created_activities = []
    
    # Créer un dictionnaire pour accéder facilement aux catégories par nom
    categories_dict = {cat.name: cat for cat in categories}
    
    for act_data in activities_data:
        # Vérifier si l'activité existe déjà
        existing_activity = Activity.objects(title=act_data["title"]).first()
        if existing_activity:
            print(f"L'activité '{act_data['title']}' existe déjà.")
            created_activities.append(existing_activity)
            continue
        
        # Récupérer la catégorie associée
        category = categories_dict.get(act_data["category_name"])
        if not category:
            print(f"Catégorie '{act_data['category_name']}' non trouvée. Activité ignorée.")
            continue
        
        # Créer la nouvelle activité
        activity = Activity(
            title=act_data["title"],
            description=act_data["description"],
            price=act_data["price"],
            duration=act_data["duration"],
            location=act_data["location"],
            category=category,
            max_participants=act_data["max_participants"]
        )
        activity.save()
        created_activities.append(activity)
        print(f"Activité '{act_data['title']}' créée avec succès.")
    
    return created_activities

def create_time_slots(activities):
    """Supprimer les créneaux"""
    print("Suppression des créneaux...")
    TimeSlot.objects.all().delete()

    """Créer des créneaux horaires pour les activités"""
    print("Création des créneaux horaires...")
    
    created_slots = []
    now = datetime.now()
    
    # Créer des créneaux pour les 14 prochains jours
    for activity in activities:
        print(f"Création de créneaux pour '{activity.title}'...")
        
        # Déterminer le nombre de créneaux par jour en fonction de l'activité
        # (certaines activités ont moins de créneaux disponibles)
        if activity.duration >= 240:  # Activités de 4h ou plus
            slots_per_day = 1
        elif activity.duration >= 180:  # Activités de 3h ou plus
            slots_per_day = 2
        else:  # Activités plus courtes
            slots_per_day = 3
        
        for day in range(1, 15):  # Les 14 prochains jours
            day_date = now + timedelta(days=day)
            
            # Générer des heures de début en fonction du nombre de créneaux
            start_hours = []
            if slots_per_day == 1:
                start_hours = [10]  # Un seul créneau à 10h
            elif slots_per_day == 2:
                start_hours = [9, 14]  # Deux créneaux: 9h et 14h
            else:
                start_hours = [9, 13, 16]  # Trois créneaux: 9h, 13h et 16h
            
            for hour in start_hours:
                # Créer le créneau horaire
                start_time = day_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(minutes=activity.duration)
                
                # Vérifier si ce créneau existe déjà
                existing_slot = TimeSlot.objects(activity=activity, start_time=start_time).first()
                if existing_slot:
                    created_slots.append(existing_slot)
                    continue
                
                # Définir un nombre aléatoire de places disponibles
                # (pour simuler des créneaux plus ou moins remplis)
                available_slots = random.randint(1, activity.max_participants)
                
                time_slot = TimeSlot(
                    activity=activity,
                    start_time=start_time,
                    end_time=end_time,
                    available_slots=available_slots
                )
                time_slot.save()
                created_slots.append(time_slot)
        
        print(f"Créneaux horaires créés pour '{activity.title}'.")
    
    return created_slots

def main():
    """Fonction principale d'initialisation de la base de données"""
    print("Initialisation de la base de données...")
    
    # Se connecter à la base de données
    connect_to_db()
    
    # Créer les utilisateurs
    admin = create_admin_user()
    test_user = create_test_user()
    
    # Créer les catégories
    categories = create_categories()
    
    # Créer les activités
    activities = create_activities(categories)
    
    # Créer les créneaux horaires
    time_slots = create_time_slots(activities)
    
    print("\nInitialisation terminée avec succès!")
    print(f"Utilisateurs créés: {len([admin, test_user])}")
    print(f"Catégories créées: {len(categories)}")
    print(f"Activités créées: {len(activities)}")
    print(f"Créneaux horaires créés: {len(time_slots)}")
    print("\nVous pouvez maintenant vous connecter avec:")
    print("Admin: admin@example.com / admin123")
    print("Utilisateur: user@example.com / user123")

if __name__ == "__main__":
    main()
