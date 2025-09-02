from src.models.user import db
from datetime import datetime
import json

class PublishedCard(db.Model):
    """上架名片資料模型"""
    __tablename__ = 'published_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    card_id = db.Column(db.String(50), unique=True, nullable=False)  # 公開的名片ID
    title = db.Column(db.String(200), nullable=False)  # 名片標題
    card_data = db.Column(db.Text, nullable=False)  # 名片JSON資料
    share_url = db.Column(db.String(500), nullable=False)  # 分享連結
    view_count = db.Column(db.Integer, default=0)  # 瀏覽次數
    is_active = db.Column(db.Boolean, default=True)  # 是否啟用
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯到客戶資料
    customer = db.relationship('Customer', backref=db.backref('published_cards', lazy=True))
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'card_id': self.card_id,
            'title': self.title,
            'card_data': json.loads(self.card_data) if self.card_data else {},
            'share_url': self.share_url,
            'view_count': self.view_count,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'customer': self.customer.to_dict() if self.customer else None
        }
    
    @staticmethod
    def from_dict(data):
        """從字典建立物件"""
        return PublishedCard(
            customer_id=data.get('customer_id'),
            card_id=data.get('card_id'),
            title=data.get('title'),
            card_data=json.dumps(data.get('card_data', {}), ensure_ascii=False),
            share_url=data.get('share_url'),
            view_count=data.get('view_count', 0),
            is_active=data.get('is_active', True)
        )

