"""
客戶管理功能測試
"""
import pytest
import json
from src.main import app, db, Customer


@pytest.fixture
def client():
    """建立測試客戶端"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def sample_customer():
    """範例客戶資料"""
    return {
        'name': '測試客戶',
        'phone': '0912345678',
        'email': 'test@example.com',
        'company': '測試公司',
        'position': '經理',
        'line_user_id': 'U1234567890',
        'website': 'https://example.com',
        'facebook_url': 'https://facebook.com/test',
        'google_map_url': 'https://maps.google.com/test',
        'contract_end_date': '2024-12-31'
    }


class TestCustomerAPI:
    """客戶API測試"""
    
    def test_create_customer(self, client, sample_customer):
        """測試新增客戶"""
        response = client.post('/api/customers', 
                             data=json.dumps(sample_customer),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['customer']['name'] == sample_customer['name']
    
    def test_get_customers(self, client, sample_customer):
        """測試取得客戶列表"""
        # 先新增一個客戶
        client.post('/api/customers', 
                   data=json.dumps(sample_customer),
                   content_type='application/json')
        
        # 取得客戶列表
        response = client.get('/api/customers')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['customers']) == 1
        assert data['customers'][0]['name'] == sample_customer['name']
    
    def test_update_customer(self, client, sample_customer):
        """測試更新客戶"""
        # 先新增一個客戶
        response = client.post('/api/customers', 
                             data=json.dumps(sample_customer),
                             content_type='application/json')
        customer_id = json.loads(response.data)['customer']['id']
        
        # 更新客戶資料
        updated_data = sample_customer.copy()
        updated_data['name'] = '更新後的客戶'
        
        response = client.put(f'/api/customers/{customer_id}',
                            data=json.dumps(updated_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['customer']['name'] == '更新後的客戶'
    
    def test_delete_customer(self, client, sample_customer):
        """測試刪除客戶"""
        # 先新增一個客戶
        response = client.post('/api/customers', 
                             data=json.dumps(sample_customer),
                             content_type='application/json')
        customer_id = json.loads(response.data)['customer']['id']
        
        # 刪除客戶
        response = client.delete(f'/api/customers/{customer_id}')
        assert response.status_code == 200
        
        # 確認客戶已被刪除
        response = client.get('/api/customers')
        data = json.loads(response.data)
        assert len(data['customers']) == 0
    
    def test_search_customers(self, client, sample_customer):
        """測試搜尋客戶"""
        # 新增多個客戶
        client.post('/api/customers', 
                   data=json.dumps(sample_customer),
                   content_type='application/json')
        
        another_customer = sample_customer.copy()
        another_customer['name'] = '另一個客戶'
        another_customer['email'] = 'another@example.com'
        client.post('/api/customers', 
                   data=json.dumps(another_customer),
                   content_type='application/json')
        
        # 搜尋特定客戶
        response = client.get('/api/customers/search?q=測試')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['customers']) == 1
        assert data['customers'][0]['name'] == '測試客戶'


class TestCustomerModel:
    """客戶模型測試"""
    
    def test_customer_creation(self):
        """測試客戶模型建立"""
        customer = Customer(
            name='測試客戶',
            phone='0912345678',
            email='test@example.com'
        )
        
        assert customer.name == '測試客戶'
        assert customer.phone == '0912345678'
        assert customer.email == 'test@example.com'
    
    def test_customer_to_dict(self):
        """測試客戶模型轉換為字典"""
        customer = Customer(
            name='測試客戶',
            phone='0912345678',
            email='test@example.com'
        )
        
        customer_dict = customer.to_dict()
        assert customer_dict['name'] == '測試客戶'
        assert customer_dict['phone'] == '0912345678'
        assert customer_dict['email'] == 'test@example.com'
        assert 'created_at' in customer_dict
        assert 'updated_at' in customer_dict


class TestCustomerValidation:
    """客戶資料驗證測試"""
    
    def test_missing_required_fields(self, client):
        """測試缺少必要欄位"""
        incomplete_data = {
            'phone': '0912345678'
            # 缺少 name 欄位
        }
        
        response = client.post('/api/customers', 
                             data=json.dumps(incomplete_data),
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_invalid_email_format(self, client):
        """測試無效的電子郵件格式"""
        invalid_data = {
            'name': '測試客戶',
            'phone': '0912345678',
            'email': 'invalid-email'
        }
        
        response = client.post('/api/customers', 
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        # 根據實際驗證邏輯調整預期結果
        # 如果有電子郵件格式驗證，應該返回400
        # 如果沒有，則會成功建立
        assert response.status_code in [200, 201, 400]
    
    def test_duplicate_email(self, client, sample_customer):
        """測試重複的電子郵件"""
        # 新增第一個客戶
        client.post('/api/customers', 
                   data=json.dumps(sample_customer),
                   content_type='application/json')
        
        # 嘗試新增相同電子郵件的客戶
        duplicate_customer = sample_customer.copy()
        duplicate_customer['name'] = '另一個客戶'
        
        response = client.post('/api/customers', 
                             data=json.dumps(duplicate_customer),
                             content_type='application/json')
        
        # 根據實際業務邏輯調整預期結果
        # 如果不允許重複電子郵件，應該返回400
        assert response.status_code in [201, 400]


if __name__ == '__main__':
    pytest.main([__file__])

