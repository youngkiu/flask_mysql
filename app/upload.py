import os
import sys
import math
import pandas as pd
from models import Company, Language, Tag, CompanyName, TagName, CompanyTag
from app import app, db


def insert_tags(company_id, language_tags):
    df = pd.DataFrame(language_tags)
    for index, row in df.iterrows():
        tag_id = None
        for country_code in df.columns:
            tag_value = row[country_code]
            tag_name = TagName.query \
                .filter_by(
                    name=tag_value
                ) \
                .first()
            curr_tag_id = tag_name.tag_id if tag_name else False
            if tag_id is None:
                tag_id = curr_tag_id
            else:
                assert tag_id == curr_tag_id, \
                    'prev({}) != curr({}) of {}'.format(
                        tag_id, curr_tag_id, tag_value)

        assert tag_id is not None
        if tag_id is False:
            tag = Tag()
            db.session.add(tag)
            db.session.commit()
            print('tag', tag.id)

            for country_code in df.columns:
                tag_value = row[country_code]
                language = Language.query \
                    .filter_by(country_code=country_code) \
                    .first()
                if language is None:
                    language = Language(country_code)
                    db.session.add(language)
                    db.session.commit()
                # print('language', language.id)

                tag_name = TagName(tag.id, language.id, tag_value)
                db.session.add(tag_name)
                db.session.commit()
                print('tag_name', tag_name.id, tag_value)

            tag_id = tag.id
        else:
            print('already registered tag', tag_id)

        company_tag = CompanyTag(company_id, tag_id)
        db.session.add(company_tag)
        db.session.commit()


def insert_company(csv_file):
    df = pd.read_csv(csv_file)
    for index, row in df.iterrows():
        company = Company()
        db.session.add(company)
        db.session.commit()
        print('company', company.id)

        language_tags = {}
        for column in df.columns:
            value = row[column]
            if isinstance(value, float) and math.isnan(value):
                continue

            company_name_tag, country_code = column.split('_')

            language = Language.query \
                .filter_by(country_code=country_code) \
                .first()
            if language is None:
                language = Language(country_code)
                db.session.add(language)
                db.session.commit()
            # print('language', language.id)

            if company_name_tag == 'company':
                company_name = CompanyName(company.id, language.id, value)
                db.session.add(company_name)
                db.session.commit()
                print('company_name', company_name.id, value)
            elif company_name_tag == 'tag':
                language_tags[country_code] = value.split('|')
            else:
                assert False, 'Not supported column title({})'.format(column)

        insert_tags(company.id, language_tags)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'python {sys.argv[0]} csv_file_path')
        sys.exit()

    csv_file_path = os.path.normpath(sys.argv[1])
    if not os.path.isfile(csv_file_path):
        print(f'[Error] invalid file path: {csv_file_path}')
        sys.exit()

    with app.app_context():
        insert_company(csv_file_path)
