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
            date=date_obj,  # 使用 date 对象而不是字符串
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
        # 获取房间数据
        room = StudyRoom.query.get(id)
        if not room:
            return jsonify({'message': 'Room not found'}), 404
            
        # 处理时间格式并确保字段存在，不使用to_dict()
        try:
            # 手动构建响应，确保所有字段存在且格式正确
            creator_data = {}
            if hasattr(room, 'creator') and room.creator:
                creator_data = {
                    'id': room.creator.id,
                    'username': room.creator.username,
                    'email': room.creator.email
                }
            
            # 确保时间格式正确
            start_time_str = '00:00'  # 默认值
            end_time_str = '00:00'    # 默认值
            date_str = None
            
            if room.date is not None:
                try:
                    date_str = room.date.isoformat()
                except (AttributeError, ValueError):
                    date_str = str(room.date)
            
            if room.start_time is not None:
                try:
                    start_time_str = room.start_time.strftime('%H:%M')
                except (AttributeError, ValueError):
                    if isinstance(room.start_time, str):
                        start_time_str = room.start_time
                    else:
                        start_time_str = '00:00'
            
            if room.end_time is not None:
                try:
                    end_time_str = room.end_time.strftime('%H:%M') 
                except (AttributeError, ValueError):
                    if isinstance(room.end_time, str):
                        end_time_str = room.end_time
                    else:
                        end_time_str = '00:00'
            
            # 确保前端需要的所有字段都存在
            response_data = {
                'room_id': room.room_id,
                'id': f"room-{room.room_id}" if hasattr(room, 'room_id') else None,
                'name': room.name if room.name else '',
                'subject': room.description if room.description else '',
                'capacity': room.capacity if room.capacity else 0,
                'description': room.description if room.description else '',
                'participants': [],
                'host': creator_data.get('username', 'Anonymous'),
                'creator_id': room.creator_id,
                'creator': creator_data,
                'date': date_str if date_str else '',
                'start_time': start_time_str if start_time_str else "00:00",
                'end_time': end_time_str if end_time_str else "00:00",
                'location': room.location if room.location else '',
                'mode': room.mode if room.mode else ''
            }
            
            return jsonify(response_data), 200
        except Exception as serialize_error:
            print(f"Error serializing room data: {str(serialize_error)}")
            # 返回一个完全可用的具有所有需要字段的响应
            return jsonify({
                'room_id': id,
                'id': f"room-{id}",
                'name': f"Room {id}",
                'subject': '',
                'description': '',
                'capacity': 0,
                'participants': [],
                'host': 'Unknown',
                'creator_id': 0,
                'creator': {'id': 0, 'username': 'Unknown', 'email': ''},
                'date': '',
                'start_time': '00:00',
                'end_time': '00:00',
                'location': '',
                'mode': '',
                'error': f'Error: {str(serialize_error)}'
            }), 200  # 返回 200 而不是 500 以避免前端报错
    except Exception as e:
        print(f"Error in get_study_room: {str(e)}")
        # 返回一个完全可用的具有所有需要字段的响应
        return jsonify({
            'room_id': id,
            'id': f"room-{id}",
            'name': f"Error Room {id}",
            'subject': '',
            'description': '',
            'capacity': 0,
            'participants': [],
            'host': 'Unknown',
            'creator_id': 0,
            'creator': {'id': 0, 'username': 'Unknown', 'email': ''},
            'date': '',
            'start_time': '00:00',
            'end_time': '00:00',
            'location': '',
            'mode': '',
            'error': f'Error: {str(e)}'
        }), 200  # 返回 200 而不是 500 以避免前端报错

def get_all_study_rooms():
    """
Endpoint to fetch all study rooms.
    """
    try:
        # 获取所有房间
        rooms = StudyRoom.query.all()
        
        # 直接定制响应格式，而非依赖 to_dict()
        rooms_data = []
        for room in rooms:
            try:
                # 手动构建每个房间数据
                creator_data = {}
                if hasattr(room, 'creator') and room.creator:
                    creator_data = {
                        'id': room.creator.id,
                        'username': room.creator.username,
                        'email': room.creator.email
                    }
                
                # 格式化时间
                start_time_str = '00:00'
                end_time_str = '00:00'
                date_str = None
                
                if room.date is not None:
                    try:
                        date_str = room.date.isoformat()
                    except (AttributeError, ValueError):
                        date_str = str(room.date)
                
                if room.start_time is not None:
                    try:
                        start_time_str = room.start_time.strftime('%H:%M')
                    except (AttributeError, ValueError):
                        if isinstance(room.start_time, str):
                            start_time_str = room.start_time
                        else:
                            start_time_str = '00:00'
                
                if room.end_time is not None:
                    try:
                        end_time_str = room.end_time.strftime('%H:%M') 
                    except (AttributeError, ValueError):
                        if isinstance(room.end_time, str):
                            end_time_str = room.end_time
                        else:
                            end_time_str = '00:00'
                
                # 构建完整的响应
                room_data = {
                    'room_id': room.room_id,
                    'name': room.name if room.name else '',
                    'description': room.description if room.description else '',
                    'capacity': room.capacity if room.capacity else 0,
                    'creator_id': room.creator_id,
                    'creator': creator_data,
                    'host': creator_data,  # 添加 host 字段作为 creator 的别名
                    'date': date_str,
                    'start_time': start_time_str,
                    'end_time': end_time_str,
                    'location': room.location if room.location else '',
                    'mode': room.mode if room.mode else ''
                }
                
                rooms_data.append(room_data)
            except Exception as room_error:
                print(f"Error serializing room {room.room_id if hasattr(room, 'room_id') else 'unknown'}: {str(room_error)}")
                # 添加一个完整的默认数据结构以避免前端错误
                rooms_data.append({
                    'room_id': room.room_id if hasattr(room, 'room_id') else 0,
                    'name': f"Room {room.room_id if hasattr(room, 'room_id') else 'Unknown'}",
                    'description': '',
                    'capacity': 0,
                    'creator_id': 0,
                    'creator': {'id': 0, 'username': 'Unknown', 'email': ''},
                    'host': {'id': 0, 'username': 'Unknown', 'email': ''},
                    'date': None,
                    'start_time': '00:00',
                    'end_time': '00:00',
                    'location': '',
                    'mode': '',
                    'error': f'Error: {str(room_error)}'
                })
        
        # 返回所有房间数据
        return jsonify(rooms_data), 200
    except Exception as e:
        print(f"Error in get_all_study_rooms: {str(e)}")
        # 返回一个空数组而不是错误信息，避免前端解析错误
        return jsonify([]), 200

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

def delete_study_room(id):
    """
    Endpoint to delete a specific study room by its ID.
    """
    try:
        room = StudyRoom.query.get(id)
        if not room:
            return jsonify({'message': 'Room not found'}), 404
        db.session.delete(room)
        db.session.commit()
        return jsonify({'message': 'Room deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Delete failed', 'error': str(e)}), 500