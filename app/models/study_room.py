# app/models/study_room.py

from datetime import datetime, date
from app import db

class StudyRoom(db.Model):
    __tablename__ = 'study_rooms'

    room_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    capacity = db.Column(db.Integer, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    location = db.Column(db.String(255), nullable=True)
    mode = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship with posts in the study room
    posts = db.relationship('Post', backref='study_room', lazy=True)

    def __init__(self, name, capacity, creator_id, description=None, date=None, start_time=None, end_time=None, location=None, mode=None):
        self.name = name
        self.capacity = capacity
        self.creator_id = creator_id
        self.description = description
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.mode = mode

    def __repr__(self):
        return f'<StudyRoom {self.name}>'

    def to_dict(self):
        return {
            'room_id': self.room_id,
            'name': self.name,
            'description': self.description,
            'capacity': self.capacity,
            'creator_id': self.creator_id,
            'creator': {
                'id': self.creator.id,
                'username': self.creator.username,
                'email': self.creator.email
            },
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'location': self.location,
            'mode': self.mode
        }