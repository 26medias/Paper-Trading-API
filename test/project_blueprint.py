# project_blueprint.py
from flask import Blueprint, request, jsonify
from project_service import ProjectService

def create_project_blueprint(db):
    project_bp = Blueprint('project', __name__, url_prefix='/project')
    project_service = ProjectService(db)

    @project_bp.route('/create', methods=['POST'])
    def create_project():
        data = request.get_json()
        response, status = project_service.create_project(data)
        return jsonify(response), status

    @project_bp.route('/fund', methods=['POST'])
    def fund_project():
        data = request.get_json()
        response, status = project_service.fund_project(data)
        return jsonify(response), status

    @project_bp.route('/data', methods=['GET'])
    def get_project():
        project_name = request.args.get('project')
        response, status = project_service.get_project(project_name)
        return jsonify(response), status

    return project_bp
