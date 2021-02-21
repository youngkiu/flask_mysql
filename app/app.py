from flask import Flask, jsonify, abort
from flask_restx import Api, Resource, reqparse
from config import VERSION, SQLALCHEMY_DATABASE_URI, SECRET_KEY
from models import db, Company, Language, CompanyName, CompanyTag


app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)
api = Api(app,
          version=VERSION, title='Company API',
          description='A company name & tag API',
          doc='/api')


read_parser = reqparse.RequestParser()
read_parser.add_argument('name', type=str, location='args', help='Company Name')
read_parser.add_argument('tag', type=str, location='args', help='Company Tag')

write_parser = reqparse.RequestParser()
write_parser.add_argument('language', required=True,
                          type=str, location='json', help='Country Code')
write_parser.add_argument('name', required=True,
                          type=str, location='json', help='Company Name')
write_parser.add_argument('tag', required=True,
                          type=str, location='json', help='Company Tag')


@api.route('/api/company')
class ApiCompany(Resource):
    @api.expect(read_parser)
    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error'
    })
    def get(self):
        args = read_parser.parse_args()
        print(args)

        name = args['name']
        if name:
            company_name = CompanyName.query \
                .filter(CompanyName.name.like('%{}%'.format(name))) \
                .first()
            if company_name:
                return company_name.name

        tag = args['tag']
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

        abort(status=400, description='No arguments')

    @api.expect(write_parser)
    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error'
    })
    def put(self):
        args = write_parser.parse_args()
        print(args)

        country_code = args['language']
        name = args['name']
        tag = args['tag']

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

        results = {'Updated': []}
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

            results['Updated'].append({name: tag})

        print(results)
        return jsonify(results)

    @api.expect(write_parser)
    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error'
    })
    def delete(self):
        args = write_parser.parse_args()
        print(args)

        country_code = args['language']
        name = args['name']
        tag = args['tag']

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

        results = {'Deleted': []}
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

            results['Deleted'].append({name: tag})

        print(results)
        return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
