from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from forms.activity_forms import ActivityCreationForm, ActivityUpdateForm, ReviewForm, ActivitySearchForm
from models import Activity, Category, Review, TimeSlot
from utils.helpers import save_image, admin_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timezone

activity_bp = Blueprint('activity', __name__, url_prefix='/activities')

@activity_bp.route('/', methods=['GET'])
def list_activities():
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Nombre d'activités par page
    
    form = ActivitySearchForm()
    
    # Préparer la requête de base
    query = {}
    
    # Appliquer les filtres s'ils sont présents dans l'URL
    if 'search_query' in request.args and request.args.get('search_query').strip():
        search_text = request.args.get('search_query')
        query['title__icontains'] = search_text
        form.search_query.data = search_text

    if 'min_price' in request.args and request.args.get('min_price').strip():
        min_price = float(request.args.get('min_price'))
        query['price__gte'] = min_price
        form.min_price.data = min_price

    if 'max_price' in request.args and request.args.get('max_price').strip():
        max_price = float(request.args.get('max_price'))
        query['price__lte'] = max_price
        form.max_price.data = max_price

    if 'category' in request.args and request.args.get('category').strip():
        category_id = request.args.get('category')
        query['category'] = category_id
        form.category.data = category_id
        
    if 'location' in request.args and request.args.get('location').strip():
        location = request.args.get('location')
        query['location__icontains'] = location
        form.location.data = location
    
    # Exécuter la requête avec pagination
    queryset = Activity.objects(**query).order_by('title')
    total_activities = queryset.count()
    total_pages = (total_activities + per_page - 1) // per_page

    activities = queryset.skip((page - 1) * per_page).limit(per_page)

    return render_template('activities/list.html',
                           activities=activities,
                           form=form,
                           title='Découvrez nos activités',
                           page=page,
                           total_pages=total_pages)

@activity_bp.route('/<id>', methods=['GET'])
def activity_detail(id):
    activity = Activity.objects(id=id).first()  # Get the first match or None
    if not activity:
        abort(404)
    review_form = ReviewForm()
    
    # Récupérer les créneaux horaires disponibles pour cette activité
    # On ne montre que les créneaux dans le futur
    now = datetime.now(timezone.utc)
    time_slots = TimeSlot.objects(activity=activity, start_time__gt=now).order_by('start_time')
    
    return render_template('activities/detail.html', 
                          activity=activity, 
                          review_form=review_form,
                          time_slots=time_slots,
                          title=activity.title)

@activity_bp.route('/category/<category_id>', methods=['GET'])
def activities_by_category(category_id):
    category = Category.objects(id=category_id).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    activities = Activity.objects(category=category).queryset.skip((page - 1) * per_page).limit(per_page)
    
    return render_template('activities/list.html', 
                          activities=activities, 
                          category=category,
                          title=f'Activités - {category.name}')

@activity_bp.route('/search', methods=['GET', 'POST'])
def search_activities():
    form = ActivitySearchForm()
    
    if form.validate_on_submit():
        # Construire l'URL avec les paramètres de recherche
        search_params = {}
        
        if form.search_query.data:
            search_params['search_query'] = form.search_query.data
            
        if form.category.data:
            search_params['category'] = form.category.data
            
        if form.min_price.data:
            search_params['min_price'] = form.min_price.data
            
        if form.max_price.data:
            search_params['max_price'] = form.max_price.data
            
        if form.location.data:
            search_params['location'] = form.location.data
        
        # Rediriger vers la liste avec les paramètres
        return redirect(url_for('activity.list_activities', **search_params))
    
    # Si on arrive ici par GET, simplement afficher le formulaire
    return render_template('activities/search.html', form=form, title='Rechercher une activité')

@activity_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_activity():
    form = ActivityCreationForm()
    
    if form.validate_on_submit():
        # Traiter l'image si elle est fournie
        image_filename = None
        if form.image.data:
            image_filename = save_image(form.image.data)
        
        # Créer l'activité
        activity = Activity(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            duration=form.duration.data,
            location=form.location.data,
            category=form.category_id.data if form.category_id.data else None,
            max_participants=form.max_participants.data,
            image_url=image_filename if image_filename else None
        )
        activity.save()
        
        flash('L\'activité a été créée avec succès!', 'success')
        return redirect(url_for('activity.activity_detail', id=activity.id))
    
    return render_template('activities/form.html', form=form, title='Ajouter une activité')

@activity_bp.route('/<id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_activity(id):
    activity = Activity.objects(id=id).first()  # Get the first match or None
    if not activity:
        abort(404)
    form = ActivityUpdateForm()
    
    if request.method == 'GET':
        form.title.data = activity.title
        form.description.data = activity.description
        form.price.data = activity.price
        form.duration.data = activity.duration
        form.location.data = activity.location
        form.category_id.data = str(activity.category.id) if activity.category else ''
        form.max_participants.data = activity.max_participants
    
    if form.validate_on_submit():
        # Traiter l'image si elle est fournie
        if form.image.data:
            # Supprimer l'ancienne image si elle existe
            if activity.image_url:
                old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], activity.image_url)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
                    
            # Sauvegarder la nouvelle image
            image_filename = save_image(form.image.data)
            activity.image_url = image_filename
        
        # Mettre à jour les autres champs
        activity.title = form.title.data
        activity.description = form.description.data
        activity.price = form.price.data
        activity.duration = form.duration.data
        activity.location = form.location.data
        activity.category = form.category_id.data if form.category_id.data else None
        activity.max_participants = form.max_participants.data
        
        activity.save()
        
        flash('L\'activité a été mise à jour avec succès!', 'success')
        return redirect(url_for('activity.activity_detail', id=activity.id))
    
    return render_template('activities/form.html', form=form, activity=activity, title='Modifier l\'activité')

@activity_bp.route('/<id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_activity(id):
    activity = Activity.objects(id=id).first()  # Get the first match or None
    if not activity:
        abort(404)
    
    # Supprimer l'image associée si elle existe
    if activity.image_url:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], activity.image_url)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Supprimer les créneaux horaires associés
    TimeSlot.objects(activity=activity).delete()
    
    # Supprimer l'activité
    activity.delete()
    
    flash('L\'activité a été supprimée avec succès!', 'success')
    return redirect(url_for('activity.list_activities'))

@activity_bp.route('/<id>/review', methods=['POST'])
@login_required
def add_review(id):
    activity = Activity.objects(id=id).first()  # Get the first match or None
    if not activity:
        abort(404)
    form = ReviewForm()
    
    if form.validate_on_submit():
        review = Review(
            user=current_user.id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        
        # Vérifier si l'utilisateur a déjà laissé un avis
        for idx, existing_review in enumerate(activity.reviews):
            if existing_review.user.id == current_user.id:
                # Remplacer l'avis existant
                activity.reviews[idx] = review
                activity.save()
                flash('Votre avis a été mis à jour!', 'success')
                return redirect(url_for('activity.activity_detail', id=id))
        
        # Ajouter le nouvel avis
        activity.reviews.append(review)
        activity.save()
        
        flash('Merci pour votre avis!', 'success')
    else:
        flash('Une erreur s\'est produite. Veuillez réessayer.', 'danger')
        
    return redirect(url_for('activity.activity_detail', id=id))