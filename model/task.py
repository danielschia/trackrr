from database.base import db
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dashboard_id = db.Column(db.Integer, db.ForeignKey('dashboards.id'), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'), nullable=True)

    user = relationship('User', back_populates='tasks')
    dashboard = relationship('Dashboard', back_populates='tasks')
    list = relationship('List', back_populates='tasks')

    def __init__(self, title:str, description:str, user_id:int, dashboard_id:int, list_id:int):
        self.title = title
        self.description = description
        self.user_id = user_id
        self.dashboard_id = dashboard_id
        self.list_id = list_id

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'user_id': self.user_id,
            'dashboard_id': self.dashboard_id,
            'list_id': self.list_id
        }