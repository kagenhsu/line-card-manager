from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.customer import Customer, db
from src.models.published_card import PublishedCard

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customers', methods=['GET'])
def get_customers():
    """取得所有客戶列表"""
    try:
        customers = Customer.query.all()
        customer_list = []
        
        for customer in customers:
            customer_data = customer.to_dict()
            # 檢查是否有已發布的名片
            published_card = PublishedCard.query.filter_by(
                customer_id=customer.id, 
                is_active=True
            ).first()
            customer_data['has_published_card'] = published_card is not None
            customer_list.append(customer_data)
        
        return jsonify(customer_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers', methods=['POST'])
def create_customer():
    """新增客戶"""
    try:
        data = request.json
        
        # 處理合約到期日期
        contract_end_date = None
        if data.get('contract_end_date'):
            contract_end_date = datetime.strptime(data['contract_end_date'], '%Y-%m-%d').date()
        
        customer = Customer(
            name=data['name'],
            phone=data.get('phone'),
            email=data.get('email'),
            company=data.get('company'),
            position=data.get('position'),
            line_user_id=data.get('line_user_id'),
            address=data.get('address'),
            website=data.get('website'),
            facebook_url=data.get('facebook_url'),
            google_map_url=data.get('google_map_url'),
            notes=data.get('notes'),
            contract_end_date=contract_end_date
        )
        
        db.session.add(customer)
        db.session.commit()
        return jsonify(customer.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@customer_bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """取得單一客戶資料"""
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer.to_dict())

@customer_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """更新客戶資料"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.json
        
        # 更新基本資料
        customer.name = data.get('name', customer.name)
        customer.phone = data.get('phone', customer.phone)
        customer.email = data.get('email', customer.email)
        customer.company = data.get('company', customer.company)
        customer.position = data.get('position', customer.position)
        customer.line_user_id = data.get('line_user_id', customer.line_user_id)
        customer.address = data.get('address', customer.address)
        customer.website = data.get('website', customer.website)
        customer.facebook_url = data.get('facebook_url', customer.facebook_url)
        customer.google_map_url = data.get('google_map_url', customer.google_map_url)
        customer.notes = data.get('notes', customer.notes)
        
        # 處理合約到期日期
        if data.get('contract_end_date'):
            customer.contract_end_date = datetime.strptime(data['contract_end_date'], '%Y-%m-%d').date()
        elif 'contract_end_date' in data and data['contract_end_date'] is None:
            customer.contract_end_date = None
            
        customer.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(customer.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@customer_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """刪除客戶"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@customer_bp.route('/customers/search', methods=['GET'])
def search_customers():
    """搜尋客戶"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    customers = Customer.query.filter(
        Customer.name.contains(query) |
        Customer.company.contains(query) |
        Customer.phone.contains(query) |
        Customer.email.contains(query)
    ).all()
    
    return jsonify([customer.to_dict() for customer in customers])

