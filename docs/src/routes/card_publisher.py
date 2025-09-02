from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.customer import Customer
from src.models.published_card import PublishedCard
from src.services.line_service import LineService
import uuid
import json
import base64
import gzip
from urllib.parse import quote
from datetime import datetime

card_publisher_bp = Blueprint('card_publisher', __name__)

@card_publisher_bp.route('/cards/publish', methods=['POST'])
def publish_card():
    """上架名片"""
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        
        if not customer_id:
            return jsonify({'error': '客戶ID是必填項目'}), 400
        
        # 取得客戶資料
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': '找不到指定的客戶'}), 404
        
        # 生成名片資料
        line_service = LineService()
        card_data = line_service.create_business_card_flex_message(customer.to_dict())
        
        # 生成唯一的名片ID
        card_id = str(uuid.uuid4())[:8]
        
        # 壓縮名片資料
        card_json = json.dumps(card_data, ensure_ascii=False)
        compressed_data = gzip.compress(card_json.encode('utf-8'))
        encoded_data = base64.b64encode(compressed_data).decode('utf-8')
        
        # 生成分享連結
        base_url = request.host_url.rstrip('/')
        share_url = f"{base_url}/card/{card_id}"
        
        # 檢查是否已經有上架的名片
        existing_card = PublishedCard.query.filter_by(customer_id=customer_id, is_active=True).first()
        
        if existing_card:
            # 更新現有名片
            existing_card.card_data = card_json
            existing_card.share_url = share_url
            existing_card.updated_at = db.func.now()
            card_id = existing_card.card_id
        else:
            # 建立新的上架名片
            published_card = PublishedCard(
                customer_id=customer_id,
                card_id=card_id,
                title=f"{customer.name}的電子名片",
                card_data=card_json,
                share_url=share_url
            )
            db.session.add(published_card)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'card_id': card_id,
            'share_url': share_url,
            'message': '名片已成功上架'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'上架名片失敗: {str(e)}'}), 500

@card_publisher_bp.route('/cards/published', methods=['GET'])
def get_published_cards():
    """取得所有上架的名片"""
    try:
        cards = PublishedCard.query.filter_by(is_active=True).order_by(PublishedCard.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'cards': [card.to_dict() for card in cards]
        })
        
    except Exception as e:
        return jsonify({'error': f'取得上架名片失敗: {str(e)}'}), 500

@card_publisher_bp.route('/cards/published/<int:customer_id>', methods=['GET'])
def get_customer_published_card(customer_id):
    """取得指定客戶的上架名片"""
    try:
        card = PublishedCard.query.filter_by(customer_id=customer_id, is_active=True).first()
        
        if not card:
            return jsonify({'error': '找不到該客戶的上架名片'}), 404
        
        return jsonify({
            'success': True,
            'card': card.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': f'取得名片失敗: {str(e)}'}), 500

@card_publisher_bp.route('/cards/unpublish/<int:customer_id>', methods=['POST'])
def unpublish_card(customer_id):
    """下架名片"""
    try:
        card = PublishedCard.query.filter_by(customer_id=customer_id, is_active=True).first()
        
        if not card:
            return jsonify({'error': '找不到該客戶的上架名片'}), 404
        
        card.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '名片已成功下架'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'下架名片失敗: {str(e)}'}), 500



@card_publisher_bp.route('/cards/create-from-designer', methods=['POST'])
def create_card_from_designer():
    """從設計器建立名片和客戶"""
    try:
        data = request.get_json()
        
        # 必填欄位檢查
        required_fields = ['name', 'card_data']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 是必填項目'}), 400
        
        # 建立或更新客戶資料
        customer_data = {
            'name': data.get('name'),
            'phone': data.get('phone', ''),
            'email': data.get('email', ''),
            'position': data.get('position', ''),
            'company': data.get('company', ''),
            'line_user_id': data.get('line_user_id', ''),
            'address': data.get('address', ''),
            'website': data.get('website', ''),
            'facebook': data.get('facebook', ''),
            'google_map': data.get('google_map', ''),
            'contract_end_date': data.get('contract_end_date'),
            'notes': data.get('notes', '')
        }
        
        # 檢查是否已存在相同姓名和電話的客戶
        existing_customer = None
        if customer_data['phone']:
            existing_customer = Customer.query.filter_by(
                name=customer_data['name'], 
                phone=customer_data['phone']
            ).first()
        
        if existing_customer:
            # 更新現有客戶資料
            for key, value in customer_data.items():
                if value:  # 只更新有值的欄位
                    setattr(existing_customer, key, value)
            customer = existing_customer
        else:
            # 建立新客戶
            customer = Customer(**customer_data)
            db.session.add(customer)
        
        db.session.commit()
        
        # 生成唯一的名片ID
        card_id = str(uuid.uuid4())[:8]
        
        # 處理名片資料
        card_data = data.get('card_data')
        if isinstance(card_data, dict):
            card_json = json.dumps(card_data, ensure_ascii=False)
        else:
            card_json = card_data
        
        # 生成分享連結
        base_url = request.host_url.rstrip('/')
        share_url = f"{base_url}/card/{card_id}"
        
        # 檢查是否已經有上架的名片
        existing_card = PublishedCard.query.filter_by(customer_id=customer.id, is_active=True).first()
        
        if existing_card:
            # 更新現有名片
            existing_card.card_data = card_json
            existing_card.share_url = share_url
            existing_card.updated_at = datetime.now()
            card_id = existing_card.card_id
        else:
            # 建立新名片記錄
            published_card = PublishedCard(
                card_id=card_id,
                customer_id=customer.id,
                card_data=card_json,
                share_url=share_url,
                is_active=True,
                view_count=0
            )
            db.session.add(published_card)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '名片建立成功',
            'card_id': card_id,
            'customer_id': customer.id,
            'share_url': share_url,
            'customer_name': customer.name
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'建立名片失敗: {str(e)}'}), 500

@card_publisher_bp.route('/cards/update-from-designer', methods=['POST'])
def update_card_from_designer():
    """從設計器更新名片"""
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        card_data = data.get('card_data')
        
        if not customer_id or not card_data:
            return jsonify({'error': '客戶ID和名片資料是必填項目'}), 400
        
        # 取得客戶資料
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': '找不到指定的客戶'}), 404
        
        # 更新客戶資料（如果有提供）
        customer_fields = ['name', 'phone', 'email', 'position', 'company', 
                          'line_user_id', 'address', 'website', 'facebook', 
                          'google_map', 'contract_end_date', 'notes']
        
        for field in customer_fields:
            if field in data and data[field] is not None:
                setattr(customer, field, data[field])
        
        # 處理名片資料
        if isinstance(card_data, dict):
            card_json = json.dumps(card_data, ensure_ascii=False)
        else:
            card_json = card_data
        
        # 更新名片記錄
        published_card = PublishedCard.query.filter_by(customer_id=customer_id, is_active=True).first()
        
        if published_card:
            published_card.card_data = card_json
            published_card.updated_at = datetime.now()
        else:
            # 如果沒有現有名片，建立新的
            card_id = str(uuid.uuid4())[:8]
            base_url = request.host_url.rstrip('/')
            share_url = f"{base_url}/card/{card_id}"
            
            published_card = PublishedCard(
                card_id=card_id,
                customer_id=customer_id,
                card_data=card_json,
                share_url=share_url,
                is_active=True,
                view_count=0
            )
            db.session.add(published_card)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '名片更新成功',
            'card_id': published_card.card_id,
            'share_url': published_card.share_url
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新名片失敗: {str(e)}'}), 500

@card_publisher_bp.route('/cards/get-by-customer/<int:customer_id>', methods=['GET'])
def get_card_by_customer(customer_id):
    """根據客戶ID取得名片資料"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': '找不到指定的客戶'}), 404
        
        published_card = PublishedCard.query.filter_by(customer_id=customer_id, is_active=True).first()
        
        if not published_card:
            return jsonify({'error': '該客戶尚未有上架的名片'}), 404
        
        # 解析名片資料
        try:
            card_data = json.loads(published_card.card_data)
        except:
            card_data = published_card.card_data
        
        return jsonify({
            'success': True,
            'customer': customer.to_dict(),
            'card_data': card_data,
            'card_id': published_card.card_id,
            'share_url': published_card.share_url,
            'view_count': published_card.view_count,
            'created_at': published_card.created_at.isoformat() if published_card.created_at else None,
            'updated_at': published_card.updated_at.isoformat() if published_card.updated_at else None
        })
        
    except Exception as e:
        return jsonify({'error': f'取得名片資料失敗: {str(e)}'}), 500

