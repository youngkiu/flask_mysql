# https://flask.palletsprojects.com/en/1.1.x/patterns/appfactories/#factories-extensions
from flask import jsonify, abort
from flask_restx import Api, Resource, reqparse
from models import db, Company, Language, Tag, CompanyName, TagName, CompanyTag

api = Api()

get_parser = reqparse.RequestParser()
get_parser.add_argument('name', required=True, type=str, location='args')

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
delete_parser.add_argument('name', required=True,
                           type=str, location='json', help='Company Name')
delete_parser.add_argument('tag', required=True,
                           type=str, location='json', help='Company Tag')


@api.route('/company')
class ApiCompany(Resource):
    @api.expect(get_parser)
    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error'
    })
    def get(self):
        args = get_parser.parse_args()

        underscore_name = args['name'].replace('_', r'\_')
        underscore_percent_name = underscore_name.replace('%', r'\%')

        company_name = CompanyName.query \
            .filter(CompanyName.name.like('%{}%'.format(underscore_percent_name))) \
            .first()
        if company_name:
            return jsonify(company_name.name)
        else:
            return jsonify('')


@api.route('/company/tag')
class ApiCompanyTag(Resource):
    @api.expect(get_parser)
    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error'
    })
    def get(self):
        args = get_parser.parse_args()

        companies = Company.query \
            .join(CompanyTag) \
            .filter(CompanyTag.company_id == Company.id) \
            .join(Tag) \
            .filter(Tag.id == CompanyTag.tag_id) \
            .join(TagName) \
            .filter(TagName.tag_id == Tag.id) \
            .filter(TagName.name == args['name']) \
            .all()

        results = []
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
        print('add tag', tag.id)

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

        results = {'Updated': []}
        for company_name in company_names:
            company_tag = CompanyTag(company_name.company_id, tag.id)
            db.session.add(company_tag)
            db.session.commit()
            print('add company_tag', company_tag.id)
            results['Updated'].append({company_name.name: added_tags})

        return jsonify(results)

    @api.expect(delete_parser)
    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error'
    })
    def delete(self):
        args = delete_parser.parse_args()

        company_tags = CompanyTag.query \
            .join(Company) \
            .filter(Company.id == CompanyTag.company_id) \
            .join(CompanyName) \
            .filter(CompanyName.company_id == Company.id) \
            .filter(CompanyName.name == args['name']) \
            .join(Tag) \
            .filter(CompanyTag.tag_id == Tag.id) \
            .join(TagName) \
            .filter(TagName.tag_id == Tag.id) \
            .filter(TagName.name == args['tag']) \
            .all()

        results = {'Deleted': []}
        for company_tag in company_tags:
            tag_name_ids = TagName.query \
                .filter_by(
                    tag_id=company_tag.tag_id
                ) \
                .all()

            deleted_tags = []
            for tag_name_id in tag_name_ids:
                deleted_tags.append(tag_name_id.name)
            results['Deleted'].append({args['name']: deleted_tags})

            db.session.delete(company_tag)
            db.session.commit()

        return jsonify(results)
