# https://flask.palletsprojects.com/en/1.1.x/testing/
# https://werkzeug.palletsprojects.com/en/1.0.x/test/

import os
import math
import random
import pytest
import json
import pandas as pd
from random import randint
from app import app


@pytest.fixture
def client():
    client = app.test_client()
    yield client


@pytest.fixture
def db_data():
    csv_file_path = os.path.join(os.pardir, 'db', 'wanted_temp_data.csv')
    df = pd.read_csv(csv_file_path)
    yield df


def test_invalid_argument(client):
    rv = client.get('/company', follow_redirects=True)
    assert 'errors' in json.loads(rv.data.decode("utf-8"))
    rv = client.get('/company/tag', follow_redirects=True)
    assert 'errors' in json.loads(rv.data.decode("utf-8"))
    rv = client.post('/company/tag', follow_redirects=True)
    assert 'The method is not allowed for the requested URL.' == \
        json.loads(rv.data.decode("utf-8"))['message']
    rv = client.delete('/company/tag', follow_redirects=True)
    assert 'Input payload validation failed' == \
        json.loads(rv.data.decode("utf-8"))['message']


def test_auto_complete_company_name(client, db_data):
    for index, row in db_data.iterrows():
        for column in db_data.columns:
            value = row[column]
            if isinstance(value, float) and math.isnan(value):
                continue

            company_name_tag, country_code = column.split('_')
            if company_name_tag == 'company':
                start_index = random.randint(0, len(value) - 1)
                end_index = random.randint(start_index + 1, len(value))
                partial_name = value[start_index:end_index]
                rv = client.get('/company', query_string=dict(name=partial_name), follow_redirects=True)
                complete_name = json.loads(rv.data.decode("utf-8"))
                assert partial_name in complete_name


def test_search_company_by_tag_name(client, db_data):
    for index, row in db_data.iterrows():
        company_names = []
        for column in db_data.columns:
            value = row[column]
            if isinstance(value, float) and math.isnan(value):
                continue

            company_name_tag, country_code = column.split('_')
            if company_name_tag == 'company':
                company_names.append(value)
            elif company_name_tag == 'tag':
                assert company_names
                tag_names = value.split('|')
                chose_tag = random.choice(tag_names)
                rv = client.get('/company/tag', query_string=dict(name=chose_tag), follow_redirects=True)
                company_names_with_tag = json.loads(rv.data.decode("utf-8"))
                assert company_names[0] in company_names_with_tag


def test_add_n_delete_tag_of_company(client, db_data):
    num_of_company = len(db_data.index)
    chose_company_index = random.randrange(num_of_company)
    row = db_data.iloc[chose_company_index]

    company_names = []
    tag_names_list = []
    for column in db_data.columns:
        value = row[column]
        if isinstance(value, float) and math.isnan(value):
            continue

        company_name_tag, country_code = column.split('_')
        if company_name_tag == 'company':
            company_names.append(value)
        elif company_name_tag == 'tag':
            tag_names_list += value.split('|')
    assert company_names and tag_names_list

    while True:
        tag_num = random.randint(1, 100)
        tag_names = [f'{tag_lan}_{tag_num}' for tag_lan in ['태그', 'tag', 'タグ']]
        if all(tag_name not in tag_names_list for tag_name in tag_names):
            break
    print(company_names, tag_names_list, tag_names)

    # add the tag to company
    chose_name = random.choice(company_names)
    arg_data = dict(name=chose_name, tag_ko=tag_names[0], tag_en=tag_names[1], tag_ja=tag_names[2])
    rv = client.put('/company/tag', json=arg_data, follow_redirects=True)
    company_names_with_tag = json.loads(rv.data.decode("utf-8"))
    assert 'Updated' in company_names_with_tag
    updated_tag_company_list = company_names_with_tag['Updated']
    for updated_tag_company in updated_tag_company_list:
        for company_name, tag_list in updated_tag_company.items():
            assert company_name in company_names
            assert sorted(tag_list) == sorted(tag_names)

    # confirm that there is a company name
    chose_tag = random.choice(tag_names)
    rv = client.get('/company/tag', query_string=dict(name=chose_tag), follow_redirects=True)
    company_names_with_tag = json.loads(rv.data.decode("utf-8"))
    assert company_names[0] in company_names_with_tag

    # delete the tag of company
    chose_name = random.choice(company_names)
    chose_tag = random.choice(tag_names)
    arg_data = dict(name=chose_name, tag=chose_tag)
    rv = client.delete('/company/tag', json=arg_data, follow_redirects=True)
    company_names_without_tag = json.loads(rv.data.decode("utf-8"))
    assert 'Deleted' in company_names_without_tag
    deleted_tag_company_list = company_names_without_tag['Deleted']
    for deleted_tag_company in deleted_tag_company_list:
        for company_name, tag_list in deleted_tag_company.items():
            assert company_name in company_names
            assert sorted(tag_list) == sorted(tag_names)

    # confirm that there is no company name
    chose_tag = random.choice(tag_names)
    rv = client.get('/company/tag', query_string=dict(name=chose_tag), follow_redirects=True)
    company_names_with_tag = json.loads(rv.data.decode("utf-8"))
    assert company_names[0] not in company_names_with_tag
