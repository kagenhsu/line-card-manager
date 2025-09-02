from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from src.models.user import db

class AuthUser(db.Model):
    """用戶認證模型"""
    __tablename__ = 'auth_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, developer, sales, designer
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('auth_users.id'))
    
    def set_password(self, password):
        """設定密碼"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """檢查密碼"""
        return check_password_hash(self.password_hash, password)
    
    def get_role_name(self):
        """取得角色中文名稱"""
        role_names = {
            'admin': '管理員',
            'developer': '程序員', 
            'sales': '業務員',
            'designer': '美工人員'
        }
        return role_names.get(self.role, '未知角色')
    
    def get_permissions(self):
        """取得角色權限"""
        permissions = {
            'admin': {
                'customer_management': True,
                'card_design': True,
                'card_publish': True,
                'card_import': True,
                'line_config': True,
                'user_management': True,
                'system_settings': True,
                'view_statistics': True,
                'export_data': True
            },
            'developer': {
                'customer_management': True,
                'card_design': True,
                'card_publish': True,
                'card_import': True,
                'line_config': True,
                'user_management': False,
                'system_settings': True,
                'view_statistics': True,
                'export_data': True
            },
            'sales': {
                'customer_management': True,
                'card_design': False,
                'card_publish': True,
                'card_import': False,
                'line_config': False,
                'user_management': False,
                'system_settings': False,
                'view_statistics': True,
                'export_data': False
            },
            'designer': {
                'customer_management': False,
                'card_design': True,
                'card_publish': True,
                'card_import': True,
                'line_config': False,
                'user_management': False,
                'system_settings': False,
                'view_statistics': False,
                'export_data': False
            }
        }
        return permissions.get(self.role, {})
    
    def has_permission(self, permission):
        """檢查是否有特定權限"""
        return self.get_permissions().get(permission, False)
    
    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'role_name': self.get_role_name(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'permissions': self.get_permissions()
        }

class UserSession(db.Model):
    """用戶會話模型"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    user = db.relationship('AuthUser', backref='sessions')
    
    def is_expired(self):
        """檢查會話是否過期"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'ip_address': self.ip_address
        }

