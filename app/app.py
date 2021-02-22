from flask import Flask, jsonify, abort
from flask_restx import Api, Resource, reqparse
from config import VERSION, SQLALCHEMY_DATABASE_URI, SECRET_KEY
from models import db, Company, Language, Tag, CompanyName, TagName, CompanyTag


app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)
api = Api(app,
          version=VERSION, title='Company API',
          description='A company name & tag API')


get_name_parser = reqparse.RequestParser()
get_name_parser.add_argument('name', required=True, type=str, location='args')

get_tag_parser = reqparse.RequestParser()
get_tag_parser.add_argument('tag', required=True, type=str, location='args')

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


@api.route('/company')
class ApiCompany(Resource):
    @api.expect(get_name_parser)
    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error'
    })
    def get(self):
        args = get_name_parser.parse_args()

        company_name = CompanyName.query \
            .filter(CompanyName.name.like('%{}%'.format(args['name']))) \
            .first()
        if company_name:
            return jsonify(company_name.name)
        else:
            return jsonify('')


@api.route('/company/tag')
class ApiCompanyTag(Resource):
    @api.expect(get_tag_parser)
    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error'
    })
    def get(self):
        args = get_tag_parser.parse_args()

        tag_names = TagName.query \
            .filter_by(name=args['tag']) \
            .all()

        results = []
        for tag_name in tag_names:
            companies = Company.query \
                .join(CompanyTag) \
                .filter(CompanyTag.tag_id == tag_name.tag_id) \
                .all()

            for company in companies:
                company_name = CompanyName.query \
                    .filter_by(company_id=company.id) \
                    .order_by(CompanyName.language_id) \
                    .first()
                results.append(company_name.name)

        return jsonify(results)

    @api.expect(put_parser)
    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error'
    })
    def put(self):
        args = put_parser.parse_args()

        company_names = CompanyName.query \
            .filter_by(name=args['name']) \
            .all()
        if not company_names:
            abort(status=400, description='Not found company name')

        tag = Tag()
        db.session.add(tag)
        db.session.commit()
        print('tag', tag.id)

        added_tags = []
        for tag_lang in ['tag_ko', 'tag_en', 'tag_ja']:
            _, country_code = tag_lang.split('_')

            language = Language.query \
                .filter_by(country_code=country_code) \
                .first()

            added_tags.append(args[tag_lang])
            tag_name = TagName(tag.id, language.id, args[tag_lang])
            db.session.add(tag_name)
            db.session.commit()
            print('tag_name', tag_name.id)

        results = {'Updated': []}
        for company_name in company_names:
            company_tag = CompanyTag(company_name.company_id, tag.id)
            db.session.add(company_tag)
            db.session.commit()
            results['Updated'].append({company_name.name: added_tags})

        return jsonify(results)

    @api.expect(delete_parser)
    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error'
    })
    def delete(self):
        args = delete_parser.parse_args()

        company_names = CompanyName.query \
            .filter_by(name=args['name']) \
            .all()
        if not company_names:
            abort(status=400, description='Not found company name')

        tag_names = TagName.query \
            .filter_by(name=args['tag']) \
            .all()
        if not tag_names:
            abort(status=400, description='Not found tag name')

        results = {'Deleted': []}
        for tag_name in tag_names:
            for company_name in company_names:
                company_tag = CompanyTag.query \
                    .filter_by(
                        company_id=company_name.company_id,
                        tag_id=tag_name.tag_id,
                    ) \
                    .first()

                if company_tag:
                    db.session.delete(company_tag)
                    db.session.commit()
                    print('company_tag', company_tag.id)

            company_tag_count = CompanyTag.query \
                .filter_by(
                    tag_id=tag_name.tag_id,
                ) \
                .count()

            if company_tag_count == 0:
                TagName.query \
                    .filter_by(
                        tag_id=tag_name.tag_id
                    ) \
                    .delete()
                db.session.commit()
                tag = Tag.query \
                    .filter_by(
                        id=tag_name.tag_id
                    ) \
                    .first()
                db.session.delete(tag)
                db.session.commit()
                print('tag', tag.id)

            results['Deleted'].append({args['name']: args['tag']})

        return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
