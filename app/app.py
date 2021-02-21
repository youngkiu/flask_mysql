from flask import Flask, jsonify, abort
from flask_restx import Api, Resource, reqparse
from config import VERSION, SQLALCHEMY_DATABASE_URI, SECRET_KEY
from models import db, Company, Language, Tag, CompanyName, CompanyTag


app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)
api = Api(app,
          version=VERSION, title='Company API',
          description='A company name & tag API',
          doc='/api')


get_parser = reqparse.RequestParser()
get_parser.add_argument('name', type=str, location='args', help='Company Name')
get_parser.add_argument('tag', type=str, location='args', help='Company Tag')

put_parser = reqparse.RequestParser()
put_parser.add_argument('name', required=True,
                        type=str, location='json', help='Company Name')
put_parser.add_argument('tag_ko', required=True,
                        type=str, location='json', help='Company Tag (country code: ko)')
put_parser.add_argument('tag_en', required=True,
                        type=str, location='json', help='Company Tag (country code: en)')
put_parser.add_argument('tag_ja', required=True,
                        type=str, location='json', help='Company Tag (country code: ja)')

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('name', required=True, type=str, location='json', help='Company Name')
delete_parser.add_argument('tag', required=True, type=str, location='json', help='Company Tag')

@api.route('/api/company')
class ApiCompany(Resource):
    @api.expect(get_parser)
    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error'
    })
    def get(self):
        args = get_parser.parse_args()

        if args['name']:
            company_name = CompanyName.query \
                .filter(CompanyName.value.like('%{}%'.format(args['name']))) \
                .first()
            if company_name:
                return jsonify(company_name.value)

        if args['tag']:
            companies = Company.query \
                .join(CompanyTag) \
                .filter(CompanyTag.value == args['tag']) \
                .all()

            results = []
            for company in companies:
                company_name = CompanyName.query \
                    .filter_by(company_id=company.id) \
                    .order_by(CompanyName.language_id) \
                    .first()
                results.append(company_name.value)

            return jsonify(results)

        abort(status=400, description='No arguments')

    @api.expect(put_parser)
    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error'
    })
    def put(self):
        args = put_parser.parse_args()

        company_names = CompanyName.query \
            .filter_by(value=args['name']) \
            .all()
        if not company_names:
            abort(status=400, description='Not found company name')

        tag = Tag()
        db.session.add(tag)
        db.session.commit()
        print('tag', tag.id)

        results = {'Updated': []}
        for company_name in company_names:
            added_tags = []
            for tag_lang in ['tag_ko', 'tag_en', 'tag_ja']:
                _, country_code = tag_lang.split('_')

                language = Language.query \
                    .filter_by(country_code=country_code) \
                    .first()

                added_tags.append(args[tag_lang])
                company_tag = CompanyTag(company_name.company_id, language.id, tag.id, args[tag_lang])
                db.session.add(company_tag)
                db.session.commit()
                print('company_tag', company_tag.id)

            results['Updated'].append({args['name']: added_tags})

        return jsonify(results)

    @api.expect(delete_parser)
    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error'
    })
    def delete(self):
        args = delete_parser.parse_args()

        company_names = CompanyName.query \
            .filter_by(value=args['name']) \
            .all()
        if not company_names:
            abort(status=400, description='Not found company name')

        results = {'Deleted': []}
        for company_name in company_names:
            company_tags = CompanyTag.query \
                .filter_by(
                    company_id=company_name.company_id,
                    value=args['tag']
                ) \
                .all()
            delted_tags = []
            for company_tag in company_tags:
                tags = CompanyTag.query \
                    .filter_by(
                        tag_id=company_tag.tag_id
                    )
                for company_tag in tags.all():
                    delted_tags.append(company_tag.serialize['tag'])
                tags.delete()
                db.session.commit()
                print('company_tag', company_tag.id)

            results['Deleted'].append({args['name']: delted_tags})

        return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
