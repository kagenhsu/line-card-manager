#!/usr/bin/env python3
"""
LINE電子名片管理系統 - 簡化版主程式
確保能夠正常啟動的版本
"""

import os
import sys
import time
from flask import Flask, jsonify, send_from_directory, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# 建立Flask應用
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# 基本設定
app.config['SECRET_KEY'] = 'line-card-manager-secret-key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 資料庫設定
db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

# 初始化資料庫
db = SQLAlchemy(app)

# 簡化的客戶資料模型
class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    company = db.Column(db.String(100))
    position = db.Column(db.String(100))
    line_user_id = db.Column(db.String(100))
    website = db.Column(db.String(200))
    facebook = db.Column(db.String(200))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'company': self.company,
            'position': self.position,
            'line_user_id': self.line_user_id,
            'website': self.website,
            'facebook': self.facebook,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 簡化的名片資料模型
class PublishedCard(db.Model):
    __tablename__ = 'published_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)  # 移除外鍵約束
    title = db.Column(db.String(100), nullable=False)
    card_data = db.Column(db.Text, nullable=False)
    share_url = db.Column(db.String(200), unique=True, nullable=False)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'title': self.title,
            'card_data': self.card_data,
            'share_url': self.share_url,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# 健康檢查API
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'LINE電子名片管理系統運行正常',
        'timestamp': time.time(),
        'version': '1.0.0'
    })

# 客戶管理API
@app.route('/api/customers', methods=['GET'])
def get_customers():
    try:
        search = request.args.get('search', '')
        customers = Customer.query.all()
        
        if search:
            customers = Customer.query.filter(
                db.or_(
                    Customer.name.contains(search),
                    Customer.company.contains(search),
                    Customer.phone.contains(search),
                    Customer.email.contains(search)
                )
            ).all()
        
        return jsonify([customer.to_dict() for customer in customers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers', methods=['POST'])
def create_customer():
    try:
        data = request.get_json()
        
        customer = Customer(
            name=data.get('name', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            company=data.get('company', ''),
            position=data.get('position', ''),
            line_user_id=data.get('line_user_id', ''),
            website=data.get('website', ''),
            facebook=data.get('facebook', ''),
            address=data.get('address', '')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify(customer.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        customer.name = data.get('name', customer.name)
        customer.phone = data.get('phone', customer.phone)
        customer.email = data.get('email', customer.email)
        customer.company = data.get('company', customer.company)
        customer.position = data.get('position', customer.position)
        customer.line_user_id = data.get('line_user_id', customer.line_user_id)
        customer.website = data.get('website', customer.website)
        customer.facebook = data.get('facebook', customer.facebook)
        customer.address = data.get('address', customer.address)
        
        db.session.commit()
        
        return jsonify(customer.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({'message': '客戶已刪除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 名片上架API
@app.route('/api/cards/publish', methods=['POST'])
def publish_card():
    try:
        data = request.get_json()
        
        # 生成分享URL
        import uuid
        share_id = str(uuid.uuid4())[:8]
        share_url = f"/card/{share_id}"
        
        card = PublishedCard(
            customer_id=data.get('customer_id', 0),
            title=data.get('title', '電子名片'),
            card_data=str(data.get('card_data', '{}')),
            share_url=share_url
        )
        
        db.session.add(card)
        db.session.commit()
        
        return jsonify({
            'message': '名片上架成功',
            'share_url': f"http://localhost:5000{share_url}",
            'card': card.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/cards', methods=['GET'])
def get_published_cards():
    try:
        cards = PublishedCard.query.order_by(PublishedCard.created_at.desc()).all()
        return jsonify([card.to_dict() for card in cards])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 名片展示頁面
@app.route('/card/<share_id>')
def show_card(share_id):
    try:
        card = PublishedCard.query.filter_by(share_url=f'/card/{share_id}').first_or_404()
        
        # 增加瀏覽次數
        card.view_count += 1
        db.session.commit()
        
        # 返回簡單的名片展示頁面
        return f"""
        <!DOCTYPE html>
        <html lang="zh-TW">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{card.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .card {{ max-width: 400px; margin: 0 auto; background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .title {{ font-size: 24px; font-weight: bold; margin-bottom: 20px; text-align: center; color: #333; }}
                .info {{ margin-bottom: 10px; }}
                .label {{ font-weight: bold; color: #666; }}
                .value {{ color: #333; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="title">{card.title}</div>
                <div class="info">瀏覽次數: {card.view_count}</div>
                <div class="info">建立時間: {card.created_at.strftime('%Y-%m-%d %H:%M') if card.created_at else ''}</div>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"錯誤: {str(e)}", 500

# 靜態檔案服務
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path == "":
        path = "index.html"
    
    try:
        return send_from_directory(app.static_folder, path)
    except:
        # 如果檔案不存在，返回首頁
        try:
            return send_from_directory(app.static_folder, 'index.html')
        except:
            return "系統正在啟動中...", 200

# 初始化資料庫
def init_db():
    """初始化資料庫"""
    try:
        with app.app_context():
            db.create_all()
            print("✅ 資料庫初始化完成")
            return True
    except Exception as e:
        print(f"❌ 資料庫初始化失敗: {e}")
        return False

if __name__ == '__main__':
    print("🚀 啟動 LINE電子名片管理系統...")
    
    # 初始化資料庫
    if init_db():
        print("🌐 伺服器啟動中...")
        print("📱 管理後台: http://localhost:5000")
        print("🎨 專業設計器: http://localhost:5000/flex-card-builder.html")
        print("🖼️ 名片展示廊: http://localhost:5000/card-gallery.html")
        print("✏️ 簡易設計器: http://localhost:5000/card-builder.html")
        print("=" * 50)
        
        try:
            app.run(host='0.0.0.0', port=5000, debug=False)
        except Exception as e:
            print(f"❌ 伺服器啟動失敗: {e}")
            print("💡 可能的解決方案:")
            print("   1. 檢查端口5000是否被占用")
            print("   2. 嘗試使用不同的端口")
            print("   3. 檢查防火牆設定")
    else:
        print("❌ 系統啟動失敗")
        input("按 Enter 鍵退出...")

