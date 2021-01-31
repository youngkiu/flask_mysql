from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Note(db.Model):
    __tablename__ = "note"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    content = db.Column(db.Text)

    def __init__(self, title, content):
        self.title = title
        self.content = content

    @property
    def serialize(self):
       return {
           'id': self.id,
           'title': self.title,
           'content': self.content
       }
