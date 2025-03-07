from flask import Blueprint, jsonify, request 
from todo.models import db 
from todo.models.todo import Todo 
from datetime import datetime, timedelta
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}

ALLOWED_FIELDS = {'title', 'description', 'completed', 'deadline_at', 'created_at', 'updated_at'}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET']) 
def get_todos(): 
    window = request.args.get('window', type=int)
    completed = request.args.get('completed', type=str)

    query = Todo.query

    if window is not None:
        now = datetime.utcnow()
        max_date = now + timedelta(days=window)
        query = query.filter(Todo.deadline_at < max_date)

    if completed is not None:
        completed = completed.lower() == 'true'
        query = query.filter(Todo.completed == completed)

    todos = query.all()
    return jsonify([todo.to_dict() for todo in todos])


@api.route('/todos/<int:todo_id>', methods=['GET']) 
def get_todo(todo_id): 
   todo = Todo.query.get(todo_id) 
   if todo is None: 
      return jsonify({'error': 'Todo not found'}), 404 
   return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST']) 
def create_todo():
    if 'title' not in request.json:
        return jsonify({"error": "Missing required fields: title"}), 400

    extra_fields = set(request.json.keys()) - ALLOWED_FIELDS
    if extra_fields:
        return jsonify({"error": f"Unexpected fields: {', '.join(extra_fields)}"}), 400 
    
    todo = Todo( 
        title=request.json.get('title'), 
        description=request.json.get('description'), 
        completed=request.json.get('completed', False), 
    ) 
    if 'deadline_at' in request.json: 
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at')) 

    db.session.add(todo) 
    db.session.commit() 

    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT']) 
def update_todo(todo_id): 
    todo = Todo.query.get(todo_id) 
    if todo is None: 
        return jsonify({'error': 'Todo not found'}), 404 
   
    extra_fields = set(request.json.keys()) - ALLOWED_FIELDS
    if extra_fields:
        return jsonify({"error": f"Unexpected fields: {', '.join(extra_fields)}"}), 400
 
    todo.title = request.json.get('title', todo.title) 
    todo.description = request.json.get('description', todo.description) 
    todo.completed = request.json.get('completed', todo.completed) 
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at) 
    db.session.commit() 

    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE']) 
def delete_todo(todo_id): 
   todo = Todo.query.get(todo_id) 
   if todo is None: 
      return jsonify({}), 200 
 
   db.session.delete(todo) 
   db.session.commit() 
   return jsonify(todo.to_dict()), 200
 
