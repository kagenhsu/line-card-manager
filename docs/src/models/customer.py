from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    company = db.Column(db.String(200), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    line_user_id = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(200), nullable=True)
    facebook_url = db.Column(db.String(200), nullable=True)
    google_map_url = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    contract_end_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Customer {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'company': self.company,
            'position': self.position,
            'line_user_id': self.line_user_id,
            'address': self.address,
            'website': self.website,
            'facebook_url': self.facebook_url,
            'google_map_url': self.google_map_url,
            'notes': self.notes,
            'contract_end_date': self.contract_end_date.isoformat() if self.contract_end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

