from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


db = SQLAlchemy()


class Language(db.Model):
    __tablename__ = 'language'

    id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, country_code):
        self.country_code = country_code


class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.now)


class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True, index=True)
    created = db.Column(db.DateTime, default=datetime.now)


class CompanyName(db.Model):
    __tablename__ = 'company_name'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), index=True)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), index=True)
    name = db.Column(db.String(100), index=True)
    created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, company_id, language_id, name):
        self.company_id = company_id
        self.language_id = language_id
        self.name = name


class TagName(db.Model):
    __tablename__ = 'tag_name'

    id = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), index=True)
    name = db.Column(db.String(100), index=True)
    created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, tag_id, language_id, name):
        self.tag_id = tag_id
        self.language_id = language_id
        self.name = name

    @property
    def serialize(self):
        return {
            'tag': self.name
        }


class CompanyTag(db.Model):
    __tablename__ = 'company_tag'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), index=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), index=True)
    created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, company_id, tag_id):
        self.company_id = company_id
        self.tag_id = tag_id
