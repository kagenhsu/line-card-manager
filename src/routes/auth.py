from flask import Blueprint, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
from src.models.auth_user import AuthUser, UserSession, db
import secrets
import hashlib

auth_bp = Blueprint('auth', __name__)

def generate_session_token():
    """生成會話令牌"""
    return secrets.token_urlsafe(32)

def get_current_user():
    """取得當前登入用戶"""
    session_token = session.get('session_token')
    if not session_token:
        return None
    
    user_session = UserSession.query.filter_by(
        session_token=session_token,
        is_active=True
    ).first()
    
    if not user_session or user_session.is_expired():
        return None
    
    return user_session.user

def require_login(f):
    """登入裝飾器"""
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': '請先登入', 'redirect': '/login.html'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_permission(permission):
    """權限檢查裝飾器"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': '請先登入', 'redirect': '/login.html'}), 401
            if not user.has_permission(permission):
                return jsonify({'error': '權限不足'}), 403
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['POST'])
def login():
    """用戶登入"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '請輸入用戶名和密碼'}), 400
        
        # 查找用戶
        user = AuthUser.query.filter_by(username=username, is_active=True).first()
        if not user or not user.check_password(password):
            return jsonify({'error': '用戶名或密碼錯誤'}), 401
        
        # 創建會話
        session_token = generate_session_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)  # 24小時過期
        
        user_session = UserSession(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        db.session.add(user_session)
        
        # 更新最後登入時間
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 設定會話
        session['session_token'] = session_token
        session['user_id'] = user.id
        
        return jsonify({
            'message': '登入成功',
            'user': user.to_dict(),
            'redirect': '/'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用戶登出"""
    try:
        session_token = session.get('session_token')
        if session_token:
            # 停用會話
            user_session = UserSession.query.filter_by(session_token=session_token).first()
            if user_session:
                user_session.is_active = False
                db.session.commit()
        
        # 清除會話
        session.clear()
        
        return jsonify({'message': '登出成功', 'redirect': '/login.html'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/current-user', methods=['GET'])
def current_user():
    """取得當前用戶資訊"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '未登入'}), 401
    
    return jsonify({'user': user.to_dict()})

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """檢查認證狀態"""
    user = get_current_user()
    return jsonify({
        'authenticated': user is not None,
        'user': user.to_dict() if user else None
    })

@auth_bp.route('/users', methods=['GET'])
@require_permission('user_management')
def get_users():
    """取得所有用戶列表（僅管理員）"""
    try:
        users = AuthUser.query.all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users', methods=['POST'])
@require_permission('user_management')
def create_user():
    """建立新用戶（僅管理員）"""
    try:
        data = request.json
        current_user = get_current_user()
        
        # 檢查必要欄位
        required_fields = ['username', 'email', 'password', 'full_name', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必要欄位: {field}'}), 400
        
        # 檢查用戶名是否已存在
        if AuthUser.query.filter_by(username=data['username']).first():
            return jsonify({'error': '用戶名已存在'}), 400
        
        # 檢查郵箱是否已存在
        if AuthUser.query.filter_by(email=data['email']).first():
            return jsonify({'error': '郵箱已存在'}), 400
        
        # 檢查角色是否有效
        valid_roles = ['admin', 'developer', 'sales', 'designer']
        if data['role'] not in valid_roles:
            return jsonify({'error': '無效的角色'}), 400
        
        # 建立新用戶
        user = AuthUser(
            username=data['username'],
            email=data['email'],
            full_name=data['full_name'],
            role=data['role'],
            created_by=current_user.id
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': '用戶建立成功',
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_permission('user_management')
def update_user(user_id):
    """更新用戶資訊（僅管理員）"""
    try:
        user = AuthUser.query.get_or_404(user_id)
        data = request.json
        
        # 更新允許的欄位
        if 'email' in data:
            # 檢查郵箱是否已被其他用戶使用
            existing_user = AuthUser.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': '郵箱已被使用'}), 400
            user.email = data['email']
        
        if 'full_name' in data:
            user.full_name = data['full_name']
        
        if 'role' in data:
            valid_roles = ['admin', 'developer', 'sales', 'designer']
            if data['role'] not in valid_roles:
                return jsonify({'error': '無效的角色'}), 400
            user.role = data['role']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': '用戶更新成功',
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_permission('user_management')
def delete_user(user_id):
    """刪除用戶（僅管理員）"""
    try:
        current_user = get_current_user()
        
        # 不能刪除自己
        if user_id == current_user.id:
            return jsonify({'error': '不能刪除自己的帳號'}), 400
        
        user = AuthUser.query.get_or_404(user_id)
        
        # 停用所有會話
        UserSession.query.filter_by(user_id=user_id).update({'is_active': False})
        
        # 軟刪除（設為非活躍）
        user.is_active = False
        db.session.commit()
        
        return jsonify({'message': '用戶已停用'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@require_login
def change_password():
    """修改密碼"""
    try:
        data = request.json
        current_user = get_current_user()
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({'error': '請輸入舊密碼和新密碼'}), 400
        
        if not current_user.check_password(old_password):
            return jsonify({'error': '舊密碼錯誤'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': '新密碼至少需要6個字符'}), 400
        
        current_user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': '密碼修改成功'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

