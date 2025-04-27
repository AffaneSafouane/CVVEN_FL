from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, Document):
    email = fields.EmailField(required=True, unique=True)
    password_hash = fields.StringField(required=True)
    name = fields.StringField(required=True)
    role = fields.StringField(choices=('user', 'admin'), default='user')
    created_at = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
class Review(EmbeddedDocument):
    user = fields.ReferenceField('User', required=True)
    rating = fields.IntField(min_value=1, max_value=5, required=True)
    comment = fields.StringField()
    created_at = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))

class Category(Document):
    name = fields.StringField(required=True, unique=True)
    description = fields.StringField()
    
    meta = {
        'indexes': ['name']
    }
    
class Activity(Document):
    title = fields.StringField(required=True)
    description = fields.StringField(required=True)
    price = fields.DecimalField(required=True)
    duration = fields.IntField(required=True)  # en minutes
    location = fields.StringField(required=True)
    category = fields.ReferenceField('Category')
    max_participants = fields.IntField(default=10)
    image_url = fields.StringField()
    reviews = fields.EmbeddedDocumentListField(Review)
    created_at = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    meta = {
        'indexes': [
            'title',
            'category',
            'price',
            'location'
        ]
    }
    
    @property
    def average_rating(self):
        if not self.reviews:
            return 0
        return sum(review.rating for review in self.reviews) / len(self.reviews)
    
class TimeSlot(Document):
    activity = fields.ReferenceField('Activity', required=True)
    start_time = fields.DateTimeField(required=True)
    end_time = fields.DateTimeField(required=True)
    available_slots = fields.IntField(required=True)
    
    meta = {
        'indexes': [
            'activity',
            'start_time'
        ]
    }
    
class Reservation(Document):
    user = fields.ReferenceField('User', required=True)
    activity = fields.ReferenceField('Activity', required=True)
    time_slot = fields.ReferenceField('TimeSlot', required=True)
    participants = fields.IntField(required=True, min_value=1)
    status = fields.StringField(choices=('pending', 'confirmed', 'cancelled'), default='pending')
    created_at = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    meta = {
        'indexes': [
            'user',
            'activity',
            'time_slot',
            'status'
        ]
    }
