from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField, HiddenField
from wtforms.validators import DataRequired, NumberRange

class ReservationForm(FlaskForm):
    time_slot_id = SelectField('Date et Heure', validators=[DataRequired()], coerce=str)
    participants = IntegerField('Nombre de participants', 
                             validators=[DataRequired(), NumberRange(min=1, message="Au moins 1 participant est requis")])
    submit = SubmitField('Réserver')

    def __init__(self, time_slots=None, max_participants=1, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        
        if time_slots:
            # Format les créneaux horaires pour l'affichage
            self.time_slot_id.choices = [
                (
                    str(slot.id), 
                    f"{slot.start_time.strftime('%d/%m/%Y %H:%M')} - {slot.end_time.strftime('%H:%M')} "
                    f"({slot.available_slots} places disponibles)"
                ) 
                for slot in time_slots if slot.available_slots > 0
            ]
        
        # Ajuster le validateur pour le nombre maximum de participants
        self.participants.validators[1].max = max_participants
        self.participants.validators[1].message = f"Maximum {max_participants} participants autorisés"

class CancellationForm(FlaskForm):
    reservation_id = HiddenField('ID de la réservation')
    submit = SubmitField('Annuler la réservation')

class TimeSlotForm(FlaskForm):
    start_time = SelectField('Heure de début', validators=[DataRequired()], coerce=str)
    duration_minutes = HiddenField('Durée (minutes)')
    available_slots = IntegerField('Places disponibles', 
                                validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Ajouter un créneau horaire')
    
    def __init__(self, time_options=None, *args, **kwargs):
        super(TimeSlotForm, self).__init__(*args, **kwargs)
        
        if time_options:
            self.start_time.choices = [(time_str, time_str) for time_str in time_options]
