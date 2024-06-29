from flask import Blueprint, request, jsonify
from firebase_admin import firestore
import datetime

# Remove this line to avoid initializing Firestore prematurely
# db = firestore.client() 

project_bp = Blueprint('project', __name__, url_prefix='/project')

@project_bp.route('/create', methods=['POST'])
def create_project():
    db = firestore.client()  # Initialize Firestore client here
    data = request.get_json()
    name = data.get('name')
    cash = data.get('cash', 0) 

    if not name:
        return jsonify({'error': 'Missing "name" parameter'}), 400

    project_ref = db.collection('paper_projects').document(name)
    if project_ref.get().exists:
        return jsonify({'error': 'Project name already exists'}), 400

    project_data = {
        'create_date': datetime.datetime.now(),
        'project': name,
        'cash': cash
    }
    project_ref.set(project_data)
    return jsonify(project_data), 201

@project_bp.route('/fund', methods=['POST'])
def fund_project():
    db = firestore.client()  # Initialize Firestore client here
    data = request.get_json()
    project_name = data.get('project')
    amount = data.get('amount')

    if not project_name or amount is None:
        return jsonify({'error': 'Missing "project" or "amount" parameter'}), 400

    project_ref = db.collection('paper_projects').document(project_name)
    project_doc = project_ref.get()

    if not project_doc.exists:
        return jsonify({'error': 'Project not found'}), 404

    project_data = project_doc.to_dict()
    project_data['cash'] += amount
    project_ref.update({'cash': project_data['cash']})

    return jsonify({'cash': project_data['cash']}), 200

@project_bp.route('/data', methods=['GET'])
def get_project():
    db = firestore.client()  # Initialize Firestore client here
    project_name = request.args.get('project')

    if not project_name:
        return jsonify({'error': 'Missing "project" parameter'}), 400

    project_ref = db.collection('paper_projects').document(project_name)
    project_doc = project_ref.get()

    if not project_doc.exists:
        return jsonify({'error': 'Project not found'}), 404

    project_data = project_doc.to_dict()
    return jsonify(project_data), 200
