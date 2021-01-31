from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    abort
)
from flask_restful import (
    Api,
    Resource
)
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY
from models import db, Note


app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)


@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        note = Note(request.form['title'], request.form['content'])
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/')
def index():
    note = Note.query.all()
    return render_template('index.html', note=note)


@app.route('/edit/<id>', methods=['POST', 'GET'])
def edit(id):
    note = Note.query.get(id)
    if request.method == 'POST':
        note.title = request.form['title']
        note.content = request.form['content']
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', note=note)


@app.route('/delete/<id>', methods=['POST', 'GET'])
def delete(id):
    note = Note.query.get(id)
    db.session.delete(note)
    db.session.commit()

    return redirect(url_for('index'))


api = Api(app)

class ApiNote(Resource):
    def get(self):
        note = Note.query.all()
        return jsonify(json_list=[i.serialize for i in note])

    def post(self):
        req_data = request.get_json()
        if req_data and all(key in req_data for key in ('title', 'content')):
            note = Note(req_data['title'], req_data['content'])
            db.session.add(note)
            db.session.commit()
            return jsonify({'id': note.id})

        abort(status=400, description='Invalid request data')

class ApiNoteId(Resource):
    def get(self, id):
        note = Note.query.get(id)
        if not note:
            abort(status=404, description='Not exist ID(%s)' % id)

        return jsonify(note.serialize)

    def put(self, id):
        note = Note.query.get(id)
        if not note:
            abort(status=404, description='Not exist ID(%s)' % id)

        req_data = request.get_json()
        if req_data and all(key in req_data for key in ('title', 'content')):
            note.title = req_data['title']
            note.content = req_data['content']
            db.session.commit()
            return jsonify({'result': 'updated'})

        abort(status=400, description='Invalid request data')

    def delete(self, id):
        note = Note.query.get(id)
        if not note:
            abort(status=404, description='Not exist ID(%s)' % id)

        db.session.delete(note)
        db.session.commit()
        return jsonify({'result': 'deleted'})

api.add_resource(ApiNote, '/api/note')
api.add_resource(ApiNoteId, '/api/note/<id>')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
