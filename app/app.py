from flask import Flask, request, jsonify, abort
from flask_restful import Api,Resource
from functools import wraps
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY
from models import db, Company, Language, CompanyName, CompanyTag


app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)
api = Api(app)


def check_name_language(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


class ApiCompany(Resource):
    def get(self):
        name = request.args.get('name')
        if name:
            company_name = CompanyName.query \
                .filter(CompanyName.name.like('%{}%'.format(name))) \
                .first()
            if company_name:
                return company_name.name

        tag = request.args.get('tag')
        if tag:
            companies = Company.query \
                .join(CompanyTag) \
                .filter(CompanyTag.tag == tag) \
                .all()

            results = []
            for company in companies:
                company_name = CompanyName.query \
                    .filter_by(company_id=company.id) \
                    .order_by(CompanyName.language_id) \
                    .first()
                results.append(company_name.name)

            print(results)
            return jsonify(results)

    def put(self):
        req_data = request.get_json()
        if req_data is None or any(key not in req_data for key in ('name', 'language', 'tag')):
            abort(status=400, description='Invalid request data')

        name = req_data['name']
        country_code = req_data['language']
        tag = req_data['tag']

        company_names = CompanyName.query \
            .filter_by(name=name) \
            .all()
        print(company_names)
        if not company_names:
            abort(status=400, description='Not found company name')

        language = Language.query \
            .filter_by(country_code=country_code) \
            .first()
        if language is None:
            language = Language(country_code)
            db.session.add(language)
            db.session.commit()
            print('language', language.id)

        results = {'updated': []}
        for company_name in company_names:
            company_tag = CompanyTag.query \
                .filter_by(
                    company_id=company_name.company_id,
                    language_id=language.id,
                    tag=tag
                ) \
                .first()
            if company_tag is None:
                company_tag = CompanyTag(company_name.company_id, language.id, tag)
                db.session.add(company_tag)
                db.session.commit()
                print('company_tag', company_tag.id)

            results['updated'].append({name: tag})

        print(results)
        return jsonify(results)

    def delete(self):
        req_data = request.get_json()
        if req_data is None or any(key not in req_data for key in ('name', 'language', 'tag')):
            abort(status=400, description='Invalid request data')

        name = req_data['name']
        country_code = req_data['language']
        tag = req_data['tag']

        company_names = CompanyName.query \
            .filter_by(name=name) \
            .all()
        print(company_names)
        if not company_names:
            abort(status=400, description='Not found company name')

        language = Language.query \
            .filter_by(country_code=country_code) \
            .first()
        if language is None:
            language = Language(country_code)
            db.session.add(language)
            db.session.commit()
            print('language', language.id)

        results = {'deleted': []}
        for company_name in company_names:
            company_tag = CompanyTag.query \
                .filter_by(
                    company_id=company_name.company_id,
                    language_id=language.id,
                    tag=tag
                ) \
                .first()
            if company_tag:
                db.session.delete(company_tag)
                db.session.commit()
                print('company_tag', company_tag.id)

            results['deleted'].append({name: tag})

        print(results)
        return jsonify(results)


api.add_resource(ApiCompany, '/api/company')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
