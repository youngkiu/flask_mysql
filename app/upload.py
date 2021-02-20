import os
import sys
import math
import pandas as pd
from models import Company, Language, CompanyName, CompanyTag
from app import app, db


def insert(csv_file):
    df = pd.read_csv(csv_file)
    for index, row in df.iterrows():
        company = Company()
        db.session.add(company)
        db.session.commit()
        print('company', company.id)

        for column in df:
            value = row[column]
            if isinstance(value, float) and math.isnan(value):
                continue

            name_tag, country_code = column.split('_')

            language = Language.query \
                .filter_by(country_code=country_code) \
                .first()
            if language is None:
                language = Language(country_code)
                db.session.add(language)
                db.session.commit()
            print('language', language.id)

            if name_tag == 'company':
                company_name = CompanyName(company.id, language.id, value)
                db.session.add(company_name)
                db.session.commit()
                print(company_name, '{}: {}'.format(name_tag, value))
            elif name_tag == 'tag':
                tags = value.split('|')
                for tag in tags:
                    company_tag = CompanyTag(company.id, language.id, tag)
                    db.session.add(company_tag)
                    db.session.commit()
                    print(company_tag, '{}: {}'.format(name_tag, tag))
            else:
                assert False, 'Not supported column title({})'.format(column)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'python {sys.argv[0]} csv_file_path')
        sys.exit()

    csv_file_path = os.path.normpath(sys.argv[1])
    if not os.path.isfile(csv_file_path):
        print(f'[Error] invalid file path: {csv_file_path}')
        sys.exit()

    with app.app_context():
        insert(csv_file_path)
