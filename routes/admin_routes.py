from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from models import User, Activity, Category, TimeSlot, Reservation
from utils.helpers import admin_required
from forms.reservation_forms import TimeSlotForm
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard', methods=['GET'])
@login_required
@admin_required
def dashboard():
    # Statistiques pour le dashboard
    total_users = User.objects.count()
    total_activities = Activity.objects.count()
    total_reservations = Reservation.objects.count()
    pending_reservations = Reservation.objects(status='pending').count()
    
    # Réservations récentes
    recent_reservations = Reservation.objects.order_by('-created_at').limit(10)
    
    # Activités les plus populaires
    # Pour simplifier, on compte juste le nombre de réservations par activité
    # Une approche plus sophistiquée calculerait le taux d'occupation
    popular_activities = []
    activities = Activity.objects()
    for activity in activities:
        reservation_count = Reservation.objects(activity=activity).count()
        popular_activities.append({
            'activity': activity,
            'reservations': reservation_count
        })
    
    # Trier par nombre de réservations
    popular_activities.sort(key=lambda x: x['reservations'], reverse=True)
    popular_activities = popular_activities[:5]  # Top 5
    
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_activities=total_activities,
        total_reservations=total_reservations,
        pending_reservations=pending_reservations,
        recent_reservations=recent_reservations,
        popular_activities=popular_activities,
        title='Dashboard Admin'
    )

@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    queryset = User.objects.order_by('name')
    total_users = queryset.count()
    total_pages = (total_users + per_page - 1) // per_page
    
    users = queryset.skip((page - 1) * per_page).limit(per_page)
    
    return render_template(
        'admin/users.html',
        users=users,
        title='Gestion des Utilisateurs',
        page=page,
        total_pages=total_pages
    )

@admin_bp.route('/users/<id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin_role(id):
    if str(current_user.id) == id:
        flash('Vous ne pouvez pas modifier votre propre rôle.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user = User.objects(id=id).first()
    if not user:
        abort(404)
    
    # Inverser le rôle
    if user.role == 'admin':
        user.role = 'user'
        message = f"L'utilisateur {user.name} n'est plus administrateur."
    else:
        user.role = 'admin'
        message = f"L'utilisateur {user.name} est maintenant administrateur."
    
    user.save()
    flash(message, 'success')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/activities', methods=['GET'])
@login_required
@admin_required
def manage_activities():
    query = {}
    page = request.args.get('page', 1, type=int)
    per_page = 15

    queryset = Activity.objects(**query).order_by('title')
    total_activities = queryset.count()
    total_pages = (total_activities + per_page - 1) // per_page

    activities = queryset.skip((page - 1) * per_page).limit(per_page)
    
    return render_template(
        'admin/activities.html',
        activities=activities,
        title='Gestion des Activités',
        page=page,
        total_pages=total_pages
    )

@admin_bp.route('/activities/<id>/time_slots', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_time_slots(id):
    activity = Activity.objects(id=id).first()
    if not activity:
        abort(404)
    
    # Générer les options d'heures pour le formulaire
    time_options = []
    start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    if start_time < datetime.now():
        start_time += timedelta(days=1)  # Commencer demain si on est déjà après 8h
    
    # Générer des créneaux de 30 minutes de 8h à 20h sur 7 jours
    for day in range(7):
        current_date = start_time + timedelta(days=day)
        for hour in range(8, 21):  # De 8h à 20h
            for minute in [0, 30]:
                slot_time = current_date.replace(hour=hour, minute=minute)
                time_str = slot_time.strftime('%Y-%m-%d %H:%M')
                time_options.append(time_str)
    
    form = TimeSlotForm(time_options=time_options)
    form.duration_minutes.data = activity.duration
    
    if form.validate_on_submit():
        start_time = datetime.strptime(form.start_time.data, '%Y-%m-%d %H:%M')
        end_time = start_time + timedelta(minutes=activity.duration)
        
        # Vérifier si un créneau similaire existe déjà
        existing_slot = TimeSlot.objects(
            activity=activity,
            start_time=start_time
        ).first()
        
        if existing_slot:
            flash('Ce créneau horaire existe déjà pour cette activité.', 'warning')
        else:
            time_slot = TimeSlot(
                activity=activity,
                start_time=start_time,
                end_time=end_time,
                available_slots=form.available_slots.data
            )
            time_slot.save()
            flash('Le créneau horaire a été ajouté avec succès.', 'success')
    
    # Récupérer tous les créneaux horaires pour cette activité
    time_slots = TimeSlot.objects(activity=activity).order_by('start_time')
    
    return render_template(
        'admin/time_slots.html',
        activity=activity,
        time_slots=time_slots,
        form=form,
        title=f'Gestion des créneaux - {activity.title}'
    )

@admin_bp.route('/time_slots/<id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_time_slot(id):
    time_slot = TimeSlot.objects(id=id).first()
    if not time_slot:
        abort(404)
    activity_id = time_slot.activity.id
    
    # Vérifier s'il y a des réservations pour ce créneau
    reservations = Reservation.objects(time_slot=time_slot)
    if reservations:
        flash('Impossible de supprimer ce créneau horaire car il contient des réservations.', 'danger')
    else:
        time_slot.delete()
        flash('Le créneau horaire a été supprimé avec succès.', 'success')
    
    return redirect(url_for('admin.manage_time_slots', id=activity_id))


@admin_bp.route('/categories', methods=['GET'])
@login_required
@admin_required
def manage_categories():
    # Get all categories
    categories = Category.objects.order_by('name')

    # Prepare a dictionary to hold the activity count for each category
    activities_by_category = {}

    # For each category, count how many activities belong to it
    for category in categories:
        # Assuming there's an `activities` field or a way to get activities for this category
        activities_count = Activity.objects(
            category=category).count()  # Adjust if needed based on your model relationships
        activities_by_category[str(category.id)] = activities_count

    # Pass the activity counts to the template
    return render_template(
        'admin/categories.html',
        categories=categories,
        activities_by_category=activities_by_category,  # Pass it here
        title='Gestion des Catégories'
    )

@admin_bp.route('/categories/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not name:
        flash('Le nom de la catégorie est requis.', 'danger')
        return redirect(url_for('admin.manage_categories'))
    
    # Vérifier si la catégorie existe déjà
    existing_category = Category.objects(name=name).first()
    if existing_category:
        flash(f'La catégorie "{name}" existe déjà.', 'warning')
        return redirect(url_for('admin.manage_categories'))
    
    # Créer la nouvelle catégorie
    category = Category(name=name, description=description)
    category.save()
    
    flash(f'La catégorie "{name}" a été ajoutée avec succès.', 'success')
    return redirect(url_for('admin.manage_categories'))

@admin_bp.route('/categories/<id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_category(id):
    category = Category.objects(id=id).first()
    if not category:
        abort(404)
    
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not name:
        flash('Le nom de la catégorie est requis.', 'danger')
        return redirect(url_for('admin.manage_categories'))
    
    # Vérifier si le nouveau nom existe déjà (sauf si c'est le même)
    if name != category.name:
        existing_category = Category.objects(name=name).first()
        if existing_category:
            flash(f'La catégorie "{name}" existe déjà.', 'warning')
            return redirect(url_for('admin.manage_categories'))
    
    # Mettre à jour la catégorie
    category.name = name
    category.description = description
    category.save()
    
    flash(f'La catégorie "{name}" a été mise à jour avec succès.', 'success')
    return redirect(url_for('admin.manage_categories'))

@admin_bp.route('/categories/<id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(id):
    category = Category.objects(id=id).first()
    if not category:
        abort(404)
    
    # Vérifier si des activités utilisent cette catégorie
    activities_with_category = Activity.objects(category=category).count()
    if activities_with_category > 0:
        flash(f'Impossible de supprimer cette catégorie car elle est utilisée par {activities_with_category} activité(s).', 'danger')
        return redirect(url_for('admin.manage_categories'))
    
    # Supprimer la catégorie
    category_name = category.name
    category.delete()
    
    flash(f'La catégorie "{category_name}" a été supprimée avec succès.', 'success')
    return redirect(url_for('admin.manage_categories'))

@admin_bp.route('/reservations', methods=['GET'])
@login_required
@admin_required
def manage_reservations():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    status_filter = request.args.get('status', '')
    user_filter = request.args.get('user', '')
    activity_filter = request.args.get('activity', '')
    
    # Construire la requête
    query = {}
    if status_filter:
        query['status'] = status_filter
    if user_filter:
        users = User.objects(name__icontains=user_filter)
        if users:
            query['user__in'] = users
    if activity_filter:
        activities = Activity.objects(title__icontains=activity_filter)
        if activities:
            query['activity__in'] = activities

    queryset = Reservation.objects(**query).order_by('-created_at')
    total_reservations = queryset.count()
    total_pages = (total_reservations + per_page - 1) // per_page

    reservations = queryset.skip((page - 1) * per_page).limit(per_page)
    
    return render_template(
        'admin/reservations.html',
        reservations=reservations,
        status_filter=status_filter,
        user_filter=user_filter,
        activity_filter=activity_filter,
        title='Gestion des Réservations',
        page=page,
        total_pages=total_pages
    )

@admin_bp.route('/reservations/<id>/update_status', methods=['POST'])
@login_required
@admin_required
def update_reservation_status(id):
    reservation = Reservation.objects(id=id).first()
    if not reservation:
        abort(404)
    new_status = request.form.get('status')
    
    if new_status not in ['pending', 'confirmed', 'cancelled']:
        flash('Statut invalide.', 'danger')
        return redirect(url_for('admin.manage_reservations'))
    
    # Si on annule une réservation qui était confirmée, remettre les places disponibles
    if new_status == 'cancelled' and reservation.status != 'cancelled':
        time_slot = reservation.time_slot
        time_slot.available_slots += reservation.participants
        time_slot.save()
    # Si on confirme une réservation qui était annulée, déduire les places
    elif new_status != 'cancelled' and reservation.status == 'cancelled':
        time_slot = reservation.time_slot
        if time_slot.available_slots >= reservation.participants:
            time_slot.available_slots -= reservation.participants
            time_slot.save()
        else:
            flash('Pas assez de places disponibles pour confirmer cette réservation.', 'danger')
            return redirect(url_for('admin.manage_reservations'))
    
    reservation.status = new_status
    reservation.save()
    
    flash('Le statut de la réservation a été mis à jour avec succès.', 'success')
    return redirect(url_for('admin.manage_reservations'))


@admin_bp.route('/reservations/<id>/delete', methods=['GET'])
@login_required
@admin_required
def delete_reservation(id):
    # Récupérer la réservation par ID
    reservation = Reservation.objects(id=id).first()
    if not reservation:
        abort(404)

    # Si la réservation est liée à une activité, vérifier si des actions supplémentaires sont nécessaires
    # (par exemple, prévenir qu'une activité liée pourrait être affectée)
    activity = reservation.activity  # Si chaque réservation a une activité associée
    if activity:
        # Exemple de condition : vous pouvez ajouter des vérifications ici si nécessaire
        flash(f'La réservation est liée à l\'activité "{activity.title}".', 'info')

    # Supprimer la réservation
    reservation_id = reservation.id
    reservation.delete()

    flash(f'La réservation avec l\'ID {reservation_id} a été supprimée avec succès.', 'success')
    return redirect(url_for('admin.manage_reservations'))

@admin_bp.route('/reports', methods=['GET'])
@login_required
@admin_required
def reports():
    # Statistiques générales
    total_users = User.objects.count()
    total_activities = Activity.objects.count()
    total_reservations = Reservation.objects.count()
    
    # Réservations par statut
    reservations_by_status = {
        'confirmed': Reservation.objects(status='confirmed').count(),
        'pending': Reservation.objects(status='pending').count(),
        'cancelled': Reservation.objects(status='cancelled').count()
    }
    
    # Activités les plus populaires
    activities = Activity.objects()
    popular_activities = []
    
    for activity in activities:
        reservation_count = Reservation.objects(activity=activity, status='confirmed').count()
        popular_activities.append({
            'activity': activity,
            'reservations': reservation_count
        })
    
    popular_activities.sort(key=lambda x: x['reservations'], reverse=True)
    popular_activities = popular_activities[:10]  # Top 10
    
    # Catégories les plus populaires
    categories = Category.objects()
    popular_categories = []
    
    for category in categories:
        category_activities = Activity.objects(category=category)
        reservation_count = Reservation.objects(activity__in=category_activities, status='confirmed').count()
        popular_categories.append({
            'category': category,
            'reservations': reservation_count
        })
    
    popular_categories.sort(key=lambda x: x['reservations'], reverse=True)
    
    return render_template(
        'admin/reports.html',
        total_users=total_users,
        total_activities=total_activities,
        total_reservations=total_reservations,
        reservations_by_status=reservations_by_status,
        popular_activities=popular_activities,
        popular_categories=popular_categories,
        title='Rapports et Statistiques'
    )
