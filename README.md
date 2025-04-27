# Site de Réservation d'Activités

Une application web complète de réservation d'activités développée avec Flask et MongoDB. Cette application permet aux utilisateurs de parcourir des activités, de faire des réservations et de laisser des avis, tout en offrant une interface d'administration pour gérer les activités, les réservations et les utilisateurs.

## Fonctionnalités

### Pour les utilisateurs
- **Inscription et connexion** : Création de compte et authentification sécurisée
- **Parcourir les activités** : Recherche et filtrage des activités par catégorie, prix et lieu
- **Réservations** : Réservation d'activités avec sélection de date, heure et nombre de participants
- **Avis et commentaires** : Possibilité de noter et commenter les activités réservées
- **Gestion du profil** : Modification des informations personnelles et historique des réservations

### Pour les administrateurs
- **Dashboard** : Aperçu général avec statistiques et informations clés
- **Gestion des activités** : Ajout, modification et suppression d'activités
- **Gestion des catégories** : Organisation des activités par catégories
- **Gestion des créneaux horaires** : Définition des disponibilités pour chaque activité
- **Gestion des réservations** : Suivi et mise à jour du statut des réservations
- **Gestion des utilisateurs** : Attribution de rôles et supervision des comptes
- **Rapports** : Statistiques détaillées sur les activités et réservations

## Architecture technique

### Backend
- **Flask** : Framework web Python léger et flexible
- **MongoDB** : Base de données NoSQL pour un stockage flexible des données
- **MongoEngine** : ODM (Object-Document Mapper) pour faciliter l'interaction avec MongoDB
- **Flask-Login** : Gestion de l'authentification utilisateur
- **Flask-WTF** : Création et validation de formulaires

### Frontend
- **Bootstrap 5** : Framework CSS responsive pour une interface moderne
- **JavaScript** : Interactivité côté client
- **Jinja2** : Moteur de templates pour le rendu HTML dynamique

## Structure du projet

```
/app
  /static
    /css
    /js
    /images
  /templates
    /auth
    /activities
    /reservations
    /admin
  /models
    models.py
  /routes
    auth_routes.py
    activity_routes.py
    reservation_routes.py
    admin_routes.py
  /forms
    auth_forms.py
    activity_forms.py
    reservation_forms.py
  /utils
    helpers.py
  config.py
  app.py
requirements.txt
README.md
```

## Installation

1. Cloner le dépôt
```
git clone https://github.com/AffaneSafouane/CVVEN_FL.git
cd CVVEN_FL
```

2. Créer un environnement virtuel et l'activer
```
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

3. Installer les dépendances
```
pip install -r requirements.txt
```

4. Configurer les variables d'environnement
```
export FLASK_APP=app.py
export FLASK_ENV=development
export SECRET_KEY=votre-clé-secrète
export MONGODB_URI=mongodb://localhost:27017/activity_booking
```

5. Lancer l'application
```
flask run
```

## Initialisation de la base de données

Pour initialiser la base de données avec des données de test, exécutez :
```
python init_db.py
```

Cela créera un utilisateur administrateur par défaut :
- Email : admin@example.com
- Mot de passe : admin123

## Déploiement

L'application peut être déployée sur n'importe quelle plateforme supportant Python, comme Heroku, AWS, ou Digital Ocean. Assurez-vous de configurer correctement les variables d'environnement sur votre serveur de production.

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou soumettre une pull request pour améliorer ce projet.

## Licence

Ce projet est sous licence MIT.
