# app/controllers/study_room_controller.py
from flask import request, jsonify
from app.models import StudyRoom
from app import db
from datetime import datetime
# Optionally, uncomment the following line if you want to check for the creator's existence.
# from app.models.user import User

def create_study_room():
    """
    Endpoint for creating a new study room.
    Expects JSON with 'name', 'capacity', 'creator_id', 'date', and 'start_time'.
    Optionally accepts 'description'.

    Enhancements:
      - Validates that 'name' is not empty.
- Validates that 'capacity' and 'creator_id' are integers.
- Optionally checks that capacity is a positive number.
- (Optional) Checks that the creator exists.
    """
    try:
        data = request.get_json()
        required_fields = ['name', 'capacity', 'creator_id', 'date', 'start_time', 'end_time', 'location', 'mode']
        if not data or not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400

        # Validate and sanitize input values
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'message': 'Study room name cannot be empty'}), 400

        try:
            capacity = int(data.get('capacity'))
        except (ValueError, TypeError):
            return jsonify({'message': 'Capacity must be an integer'}), 400

        if capacity <= 0:
            return jsonify({'message': 'Capacity must be greater than zero'}), 400

        try:
            creator_id = int(data.get('creator_id'))
        except (ValueError, TypeError):
            return jsonify({'message': 'Creator ID must be an integer'}), 400

        # Validate date field
        date_str = data.get('date', '').strip()
        if not date_str:
            return jsonify({'message': 'Date is required'}), 400
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format, expected YYYY-MM-DD'}), 400

        # Validate start_time field
        start_time_str = data.get('start_time', '').strip()
        if not start_time_str:
            return jsonify({'message': 'Start time is required'}), 400
        try:
            time_obj = datetime.strptime(start_time_str, '%H:%M').time()
            start_time = datetime.combine(date_obj, time_obj)
        except ValueError:
            return jsonify({'message': 'Invalid start_time format, expected HH:mm'}), 400

        # Validate end_time field
        end_time_str = data.get('end_time', '').strip()
        if not end_time_str:
            return jsonify({'message': 'End time is required'}), 400
        try:
            time_obj = datetime.strptime(end_time_str, '%H:%M').time()
            end_time = datetime.combine(date_obj, time_obj)
        except ValueError:
            return jsonify({'message': 'Invalid end_time format, expected HH:mm'}), 400

        # Validate location field
        location = data.get('location', '').strip()
        if not location:
            return jsonify({'message': 'Location is required'}), 400

        # Validate mode field
        mode = data.get('mode', '').strip()
        if not mode:
            return jsonify({'message': 'Mode is required'}), 400

        # Optional: Verify that the creator exists
        # user = User.query.get(creator_id)
        # if not user:
        #     return jsonify({'message': 'Creator (user) not found'}), 404

        description = data.get('description')
        if description:
            description = description.strip()

        # Create and commit the new study room
        new_room = StudyRoom(
            name=name,
            capacity=capacity,
            creator_id=creator_id,
            description=description,
            date=date_str,
            start_time=start_time,
            end_time=end_time,
            location=location,
            mode=mode
        )
        db.session.add(new_room)
        db.session.commit()

        return jsonify({'message': 'Study room created', 'room_id': new_room.room_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Creation failed', 'error': str(e)}), 500

def get_study_room(id):
    """
Endpoint to fetch a specific study room by its ID.
    """
    try:
        room = StudyRoom.query.get(id)
        if not room:
            return jsonify({'message': 'Room not found'}), 404
        return jsonify(room.to_dict()), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching room', 'error': str(e)}), 500

def get_all_study_rooms():
    """
Endpoint to fetch all study rooms.
    """
    try:
        rooms = StudyRoom.query.all()
        rooms_data = [room.to_dict() for room in rooms]
        return jsonify(rooms_data), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching rooms', 'error': str(e)}), 500

def update_study_room(id):
    """
    Endpoint to update a specific study room by its ID.
    """
    try:
        room = StudyRoom.query.get(id)
        if not room:
            return jsonify({'message': 'Room not found'}), 404
        data = request.get_json() or {}
        # Update fields if present
        if 'name' in data:
            room.name = data['name'].strip()
        if 'description' in data:
            room.description = data['description'].strip()
        if 'capacity' in data:
            try:
                room.capacity = int(data['capacity'])
            except (ValueError, TypeError):
                return jsonify({'message': 'Capacity must be an integer'}), 400
        if 'date' in data:
            date_str = data['date'].strip()
            try:
                room.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'message': 'Invalid date format, expected YYYY-MM-DD'}), 400
        if 'start_time' in data:
            st_str = data['start_time'].strip()
            try:
                time_obj = datetime.strptime(st_str, '%H:%M').time()
                room.start_time = datetime.combine(room.date, time_obj)
            except ValueError:
                return jsonify({'message': 'Invalid start_time format, expected HH:mm'}), 400
        if 'end_time' in data:
            et_str = data['end_time'].strip()
            try:
                time_obj = datetime.strptime(et_str, '%H:%M').time()
                room.end_time = datetime.combine(room.date, time_obj)
            except ValueError:
                return jsonify({'message': 'Invalid end_time format, expected HH:mm'}), 400
        if 'location' in data:
            room.location = data['location'].strip()
        if 'mode' in data:
            room.mode = data['mode'].strip()

        db.session.commit()
        return jsonify(room.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Update failed', 'error': str(e)}), 500