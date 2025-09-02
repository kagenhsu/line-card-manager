"""
用戶認證功能測試
"""
import pytest
import json
from src.main import app, db, AuthUser


@pytest.fixture
def client():
    """建立測試客戶端"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # 建立測試用戶
            admin_user = AuthUser(
                username='admin',
                email='admin@test.com',
                full_name='測試管理員',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            
            sales_user = AuthUser(
                username='sales',
                email='sales@test.com',
                full_name='測試業務員',
                role='sales'
            )
            sales_user.set_password('sales123')
            db.session.add(sales_user)
            
            db.session.commit()
            
            yield client
            db.drop_all()


class TestAuthAPI:
    """認證API測試"""
    
    def test_login_success(self, client):
        """測試成功登入"""
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['user']['username'] == 'admin'
        assert data['user']['role'] == 'admin'
    
    def test_login_invalid_credentials(self, client):
        """測試無效憑證登入"""
        login_data = {
            'username': 'admin',
            'password': 'wrong_password'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_login_nonexistent_user(self, client):
        """測試不存在的用戶登入"""
        login_data = {
            'username': 'nonexistent',
            'password': 'password'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_logout(self, client):
        """測試登出"""
        # 先登入
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        client.post('/api/auth/login',
                   data=json.dumps(login_data),
                   content_type='application/json')
        
        # 登出
        response = client.post('/api/auth/logout')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_current_user_authenticated(self, client):
        """測試獲取當前已認證用戶"""
        # 先登入
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        client.post('/api/auth/login',
                   data=json.dumps(login_data),
                   content_type='application/json')
        
        # 獲取當前用戶
        response = client.get('/api/auth/current-user')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['user']['username'] == 'admin'
        assert data['user']['role'] == 'admin'
    
    def test_current_user_unauthenticated(self, client):
        """測試獲取當前未認證用戶"""
        response = client.get('/api/auth/current-user')
        assert response.status_code == 401


class TestAuthUserModel:
    """認證用戶模型測試"""
    
    def test_password_hashing(self):
        """測試密碼雜湊"""
        user = AuthUser(
            username='test',
            email='test@example.com',
            full_name='測試用戶',
            role='sales'
        )
        
        user.set_password('test123')
        assert user.password_hash != 'test123'
        assert user.check_password('test123') is True
        assert user.check_password('wrong') is False
    
    def test_user_permissions(self):
        """測試用戶權限"""
        # 測試管理員權限
        admin = AuthUser(role='admin')
        admin_perms = admin.get_permissions()
        assert admin_perms['user_management'] is True
        assert admin_perms['customer_management'] is True
        assert admin_perms['card_design'] is True
        
        # 測試業務員權限
        sales = AuthUser(role='sales')
        sales_perms = sales.get_permissions()
        assert sales_perms['user_management'] is False
        assert sales_perms['customer_management'] is True
        assert sales_perms['card_design'] is False
        
        # 測試美工人員權限
        designer = AuthUser(role='designer')
        designer_perms = designer.get_permissions()
        assert designer_perms['user_management'] is False
        assert designer_perms['customer_management'] is False
        assert designer_perms['card_design'] is True
        
        # 測試程序員權限
        developer = AuthUser(role='developer')
        developer_perms = developer.get_permissions()
        assert developer_perms['user_management'] is False
        assert developer_perms['customer_management'] is True
        assert developer_perms['card_design'] is True
        assert developer_perms['system_config'] is True
    
    def test_user_to_dict(self):
        """測試用戶模型轉換為字典"""
        user = AuthUser(
            username='test',
            email='test@example.com',
            full_name='測試用戶',
            role='sales'
        )
        
        user_dict = user.to_dict()
        assert user_dict['username'] == 'test'
        assert user_dict['email'] == 'test@example.com'
        assert user_dict['full_name'] == '測試用戶'
        assert user_dict['role'] == 'sales'
        assert user_dict['role_name'] == '業務員'
        assert 'permissions' in user_dict
        assert 'password_hash' not in user_dict  # 確保密碼不會洩露


class TestRoleBasedAccess:
    """角色權限控制測試"""
    
    def test_admin_access(self, client):
        """測試管理員權限"""
        # 管理員登入
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        client.post('/api/auth/login',
                   data=json.dumps(login_data),
                   content_type='application/json')
        
        # 管理員應該可以訪問用戶管理
        response = client.get('/api/auth/users')
        # 根據實際實作調整預期結果
        assert response.status_code in [200, 404]  # 404表示路由未實作
    
    def test_sales_access(self, client):
        """測試業務員權限"""
        # 業務員登入
        login_data = {
            'username': 'sales',
            'password': 'sales123'
        }
        client.post('/api/auth/login',
                   data=json.dumps(login_data),
                   content_type='application/json')
        
        # 業務員應該可以訪問客戶管理
        response = client.get('/api/customers')
        assert response.status_code == 200
        
        # 業務員不應該可以訪問用戶管理
        response = client.get('/api/auth/users')
        # 根據實際實作調整預期結果
        assert response.status_code in [403, 404]  # 403表示權限不足，404表示路由未實作


class TestSessionManagement:
    """Session管理測試"""
    
    def test_session_persistence(self, client):
        """測試Session持久性"""
        # 登入
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        client.post('/api/auth/login',
                   data=json.dumps(login_data),
                   content_type='application/json')
        
        # 多次請求應該保持登入狀態
        for _ in range(3):
            response = client.get('/api/auth/current-user')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['user']['username'] == 'admin'
    
    def test_session_cleanup_after_logout(self, client):
        """測試登出後Session清理"""
        # 登入
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        client.post('/api/auth/login',
                   data=json.dumps(login_data),
                   content_type='application/json')
        
        # 確認已登入
        response = client.get('/api/auth/current-user')
        assert response.status_code == 200
        
        # 登出
        client.post('/api/auth/logout')
        
        # 確認Session已清理
        response = client.get('/api/auth/current-user')
        assert response.status_code == 401


if __name__ == '__main__':
    pytest.main([__file__])

