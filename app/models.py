from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


db = SQLAlchemy()


class Language(db.Model):
    __tablename__ = 'language'

    id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String(10), unique=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, country_code):
        self.country_code = country_code


class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.now)


class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.now)


class CompanyName(db.Model):
    __tablename__ = 'company_name'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    value = db.Column(db.String(100))
    created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, company_id, language_id, value):
        self.company_id = company_id
        self.language_id = language_id
        self.value = value


class CompanyTag(db.Model):
    __tablename__ = 'company_tag'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    value = db.Column(db.String(100))
    created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, company_id, language_id, tag_id, value):
        self.company_id = company_id
        self.language_id = language_id
        self.tag_id = tag_id
        self.value = value

    @property
    def serialize(self):
        return {
            'tag': self.value
        }
