from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:20040219@localhost:5432/sports'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

logging.basicConfig(level=logging.DEBUG)

def verify_token(token):
    try:
        response = requests.get('http://localhost:5000/user/session', headers={'Authorization': f'Bearer {token}'})
        logging.debug(f"Token verification response: {response.status_code} {response.text}")
        return response.status_code == 200
    except requests.RequestException as e:
        logging.error(f"Error verifying token: {e}")
        return False

@app.before_request
def before_request():
    token = request.headers.get('Authorization')
    logging.debug(f"Received token: {token}")
    if not token or not token.startswith('Bearer '):
        logging.warning("No token provided or token does not start with 'Bearer '")
        return jsonify(msg="无令牌提供", code=4000), 400
    token = token.split(' ')[1]
    if not verify_token(token):
        logging.warning("Invalid token")
        return jsonify(msg="无效的令牌", code=4001), 401


@app.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    new_project = Project(
        name=data['name'],
        description=data.get('description'),
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d'),
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d'),
        status=data['status']
    )
    db.session.add(new_project)
    db.session.commit()
    return jsonify({'message': 'Project created successfully'}), 201

@app.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    projects_list = [
        {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'start_date': project.start_date.strftime('%Y-%m-%d'),
            'end_date': project.end_date.strftime('%Y-%m-%d'),
            'status': project.status
        }
        for project in projects
    ]
    return jsonify(projects_list)

@app.route('/projects/<int:id>', methods=['GET'])
def get_project(id):
    project = Project.query.get(id)
    if not project:
        return jsonify(msg="项目未找到", code=404), 404
    project_data = {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'start_date': project.start_date.strftime('%Y-%m-%d'),
        'end_date': project.end_date.strftime('%Y-%m-%d'),
        'status': project.status
    }
    return jsonify(project_data)

@app.route('/projects/<int:id>', methods=['PUT'])
def update_project(id):
    data = request.get_json()
    project = Project.query.get(id)
    if not project:
        return jsonify(msg="项目未找到", code=404), 404

    project.name = data.get('name', project.name)
    project.description = data.get('description', project.description)
    project.start_date = datetime.strptime(data.get('start_date', project.start_date.strftime('%Y-%m-%d')), '%Y-%m-%d')
    project.end_date = datetime.strptime(data.get('end_date', project.end_date.strftime('%Y-%m-%d')), '%Y-%m-%d')
    project.status = data.get('status', project.status)

    db.session.commit()
    return jsonify({'message': 'Project updated successfully'})

@app.route('/projects/<int:id>', methods=['DELETE'])
def delete_project(id):
    project = Project.query.get(id)
    if not project:
        return jsonify(msg="项目未找到", code=404), 404

    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Project deleted successfully'})

@app.route('/participants', methods=['POST'])
def create_participant():
    data = request.get_json()
    new_participant = Participant(
        name=data['name'],
        email=data['email'],
        role=data['role']
    )
    db.session.add(new_participant)
    db.session.commit()
    return jsonify({'message': 'Participant created successfully'}), 201

@app.route('/participants', methods=['GET'])
def get_participants():
    participants = Participant.query.all()
    participants_list = [
        {
            'id': participant.id,
            'name': participant.name,
            'email': participant.email,
            'role': participant.role
        }
        for participant in participants
    ]
    return jsonify(participants_list)

@app.route('/participants/<int:id>', methods=['GET'])
def get_participant(id):
    participant = Participant.query.get(id)
    if not participant:
        return jsonify(msg="参与者未找到", code=404), 404
    participant_data = {
        'id': participant.id,
        'name': participant.name,
        'email': participant.email,
        'role': participant.role
    }
    return jsonify(participant_data)

@app.route('/participants/<int:id>', methods=['PUT'])
def update_participant(id):
    data = request.get_json()
    participant = Participant.query.get(id)
    if not participant:
        return jsonify(msg="参与者未找到", code=404), 404

    participant.name = data.get('name', participant.name)
    participant.email = data.get('email', participant.email)
    participant.role = data.get('role', participant.role)

    db.session.commit()
    return jsonify({'message': 'Participant updated successfully'})

@app.route('/participants/<int:id>', methods=['DELETE'])
def delete_participant(id):
    participant = Participant.query.get(id)
    if not participant:
        return jsonify(msg="参与者未找到", code=404), 404

    db.session.delete(participant)
    db.session.commit()
    return jsonify({'message': 'Participant deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)