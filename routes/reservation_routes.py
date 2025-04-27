from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from forms.reservation_forms import ReservationForm, CancellationForm
from models import Activity, TimeSlot, Reservation
from datetime import datetime, timezone

reservation_bp = Blueprint('reservation', __name__, url_prefix='/reservations')

@reservation_bp.route('/<activity_id>/book', methods=['GET', 'POST'])
@login_required
def book_activity(activity_id):
    activity = Activity.objects(id=activity_id).first()  # Get the first match or None
    if not activity:
        abort(404)
    
    # Récupérer les créneaux horaires disponibles pour cette activité
    now = datetime.now(timezone.utc)
    time_slots = TimeSlot.objects(activity=activity, start_time__gt=now, available_slots__gt=0).order_by('start_time')
    
    if not time_slots:
        flash('Aucun créneau horaire disponible pour cette activité.', 'warning')
        return redirect(url_for('activity.activity_detail', id=activity_id))
    
    form = ReservationForm(time_slots=time_slots, max_participants=activity.max_participants)
    
    if form.validate_on_submit():
        time_slot = TimeSlot.objects(id=form.time_slot_id.data).first()
        
        # Vérifier si l'utilisateur a déjà une réservation pour ce créneau
        existing_reservation = Reservation.objects(
            user=current_user.id,
            activity=activity,
            time_slot=time_slot,
            status__ne='cancelled'  # Ne pas prendre en compte les réservations annulées
        ).first()
        
        if existing_reservation:
            flash('Vous avez déjà une réservation pour ce créneau horaire.', 'warning')
            return redirect(url_for('activity.activity_detail', id=activity_id))
        
        # Vérifier s'il reste suffisamment de places
        if time_slot.available_slots < form.participants.data:
            flash(f'Il ne reste que {time_slot.available_slots} place(s) disponible(s).', 'danger')
            return redirect(url_for('reservation.book_activity', activity_id=activity_id))
        
        # Créer la réservation
        reservation = Reservation(
            user=current_user.id,
            activity=activity,
            time_slot=time_slot,
            participants=form.participants.data,
            status='confirmed'  # On pourrait aussi utiliser 'pending' et ajouter une étape de confirmation
        )
        reservation.save()
        
        # Mettre à jour le nombre de places disponibles
        time_slot.available_slots -= form.participants.data
        time_slot.save()
        
        flash('Votre réservation a été confirmée!', 'success')
        return redirect(url_for('reservation.my_reservations'))
    
    return render_template('reservations/book.html', form=form, activity=activity, title='Réserver une activité')

@reservation_bp.route('/', methods=['GET'])
@login_required
def my_reservations():
    # Récupérer les réservations de l'utilisateur, triées par date
    reservations = Reservation.objects(
        user=current_user.id
    ).order_by('-time_slot__start_time')
    
    # Séparer les réservations à venir et passées
    now = datetime.now(timezone.utc)
    upcoming = []
    past = []

    for reservation in reservations:
        # Ensure the reservation's start time is timezone-aware
        start_time = reservation.time_slot.start_time

        if start_time.tzinfo is None:  # If it's naive, make it aware
            start_time = start_time.replace(tzinfo=timezone.utc)

        # Compare the start_time with the current time (now)
        if start_time > now:
            upcoming.append(reservation)
        else:
            past.append(reservation)
    
    return render_template(
        'reservations/my_reservations.html',
        upcoming_reservations=upcoming,
        past_reservations=past,
        title='Mes Réservations'
    )

@reservation_bp.route('/<id>', methods=['GET'])
@login_required
def reservation_detail(id):
    reservation = Reservation.objects(id=id, user=current_user.id).first()  # Get the first match or None
    if not reservation:
        abort(404)
    cancellation_form = CancellationForm()
    cancellation_form.reservation_id.data = str(reservation.id)
    if reservation.time_slot.start_time.tzinfo is None:
        reservation.time_slot.start_time = reservation.time_slot.start_time.replace(tzinfo=timezone.utc)
    
    return render_template(
        'reservations/detail.html',
        reservation=reservation,
        cancellation_form=cancellation_form,
        title='Détail de la réservation'
    )

@reservation_bp.route('/<id>/cancel', methods=['GET'])
@login_required
def cancel_reservation(id):
    reservation = Reservation.objects(id=id, user=current_user.id).first()  # Get the first match or None
    if not reservation:
        abort(404)
    
    # Vérifier si la réservation peut être annulée
    if reservation.time_slot.start_time.tzinfo is None:
        reservation.time_slot.start_time = reservation.time_slot.start_time.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    if reservation.time_slot.start_time <= now:
        flash('Impossible d\'annuler une réservation qui a déjà commencé ou qui est terminée.', 'danger')
        return redirect(url_for('reservation.reservation_detail', id=id))
    
    if reservation.status == 'cancelled':
        flash('Cette réservation est déjà annulée.', 'warning')
        return redirect(url_for('reservation.my_reservations'))
    
    # Annuler la réservation
    reservation.status = 'cancelled'
    reservation.save()
    
    # Remettre les places disponibles
    time_slot = reservation.time_slot
    time_slot.available_slots += reservation.participants
    time_slot.save()
    
    flash('Votre réservation a été annulée avec succès.', 'success')
    return redirect(url_for('reservation.my_reservations'))
