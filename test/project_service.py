import datetime

class ProjectService:
    def __init__(self, db):
        self.db = db

    def create_project(self, data):
        name = data.get('name')
        cash = data.get('cash', 0)

        if not name:
            return {'error': 'Missing "name" parameter'}, 400

        project_ref = self.db.collection('paper_projects').document(name)
        if project_ref.get().exists:
            return {'error': 'Project name already exists'}, 400

        project_data = {
            'create_date': datetime.datetime.now(),
            'project': name,
            'cash': cash
        }
        project_ref.set(project_data)
        return project_data, 201

    def fund_project(self, data):
        project_name = data.get('project')
        amount = data.get('amount')

        if not project_name or amount is None:
            return {'error': 'Missing "project" or "amount" parameter'}, 400

        project_ref = self.db.collection('paper_projects').document(project_name)
        project_doc = project_ref.get()

        if not project_doc.exists:
            return {'error': 'Project not found'}, 404

        project_data = project_doc.to_dict()
        project_data['cash'] += amount
        project_ref.update({'cash': project_data['cash']})

        return {'cash': project_data['cash']}, 200

    def get_project(self, project_name):
        if not project_name:
            return {'error': 'Missing "project" parameter'}, 400

        project_ref = self.db.collection('paper_projects').document(project_name)
        project_doc = project_ref.get()

        if not project_doc.exists:
            return {'error': 'Project not found'}, 404

        project_data = project_doc.to_dict()
        return project_data, 200
