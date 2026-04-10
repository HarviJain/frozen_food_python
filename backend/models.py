from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# =========================
# Enquiry Table - Matches your database schema
# =========================
class Enquiry(db.Model):
    __tablename__ = 'enquiries'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    business_type = db.Column(db.String(100), nullable=True)
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Remove 'seen' column if it doesn't exist in your table
    # seen = db.Column(db.Boolean, default=False)  # Comment this out
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'company': self.company,
            'phone': self.phone,
            'email': self.email,
            'business_type': self.business_type,
            'message': self.message,
            'date': self.created_at.isoformat() if self.created_at else None
        }