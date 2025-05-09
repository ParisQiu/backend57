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
        try:
            # 安全地获取 creator 属性
            creator_data = {}
            if hasattr(self, 'creator') and self.creator is not None:
                creator_data = {
                    'id': self.creator.id,
                    'username': self.creator.username,
                    'email': self.creator.email
                }
            
            # 确保日期和时间能正确序列化
            date_str = ''
            start_time_str = '00:00'
            end_time_str = '00:00'
            
            if self.date is not None:
                try:
                    date_str = self.date.isoformat()
                except (AttributeError, ValueError):
                    date_str = str(self.date) if self.date else ''
                    
            if self.start_time:
                try:
                    start_time_str = self.start_time.strftime('%H:%M')
                except (AttributeError, ValueError):
                    start_time_str = str(self.start_time) if self.start_time else '00:00'
            if not start_time_str or len(start_time_str) != 5:
                start_time_str = '00:00'
            
            if self.end_time:
                try:
                    end_time_str = self.end_time.strftime('%H:%M')
                except (AttributeError, ValueError):
                    end_time_str = str(self.end_time) if self.end_time else '00:00'
            if not end_time_str or len(end_time_str) != 5:
                end_time_str = '00:00'
            
            host_name = creator_data.get('username', 'Anonymous') if creator_data else 'Anonymous'
            
            return {
                'room_id': self.room_id,
                'id': f"room-{self.room_id}",
                'name': self.name if self.name else '',
                'subject': self.description if self.description else '',
                'description': self.description if self.description else '',
                'capacity': self.capacity if self.capacity else 0,
                'participants': [],
                'host': host_name,
                'creator_id': self.creator_id,
                'creator': creator_data,
                'date': date_str,
                'start_time': start_time_str,
                'end_time': end_time_str,
                'location': self.location if self.location else '',
                'mode': self.mode if self.mode else ''
            }
        except Exception as e:
            # 如果有任何异常，返回一个简化的字典
            print(f"Error in to_dict(): {str(e)}")
            return {
                'room_id': self.room_id if hasattr(self, 'room_id') else 0,
                'id': f"room-{self.room_id if hasattr(self, 'room_id') else 0}",
                'name': self.name if hasattr(self, 'name') else '',
                'subject': '',
                'description': '',
                'capacity': 0,
                'participants': [],
                'host': 'Anonymous',
                'creator_id': self.creator_id if hasattr(self, 'creator_id') else 0,
                'creator': {'id': 0, 'username': 'Anonymous', 'email': ''},
                'date': '',
                'start_time': '00:00',
                'end_time': '00:00',
                'location': '',
                'mode': '',
                'error': 'Data serialization error'
            }