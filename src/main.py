#!/usr/bin/env python3
"""
LINE電子名片管理系統 - 簡化版主程式
確保能夠正常啟動的版本
"""

import os
import sys
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from flask import Flask, jsonify, send_from_directory, request, session
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

# 簡化的用戶認證模型
class AuthUser(db.Model):
    __tablename__ = 'auth_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='sales')  # admin, developer, sales, designer
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def set_password(self, password):
        """設定密碼"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        """檢查密碼"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def get_permissions(self):
        """獲取角色權限"""
        permissions = {
            'admin': {
                'customer_management': True,
                'card_design': True,
                'card_import': True,
                'user_management': True,
                'system_config': True,
                'statistics': True
            },
            'developer': {
                'customer_management': True,
                'card_design': True,
                'card_import': True,
                'user_management': False,
                'system_config': True,
                'statistics': True
            },
            'sales': {
                'customer_management': True,
                'card_design': False,
                'card_import': False,
                'user_management': False,
                'system_config': False,
                'statistics': True
            },
            'designer': {
                'customer_management': False,
                'card_design': True,
                'card_import': True,
                'user_management': False,
                'system_config': False,
                'statistics': False
            }
        }
        return permissions.get(self.role, permissions['sales'])
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'role_name': {
                'admin': '管理員',
                'developer': '程序員', 
                'sales': '業務員',
                'designer': '美工人員'
            }.get(self.role, '未知'),
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'permissions': self.get_permissions()
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

# 名片匯入API
@app.route('/api/cards/import', methods=['POST'])
def import_flex_card():
    """匯入現有的Flex Message名片"""
    try:
        data = request.get_json()
        
        # 驗證必要欄位
        if not data.get('flex_json'):
            return jsonify({'error': '請提供Flex Message JSON'}), 400
        
        if not data.get('card_name'):
            return jsonify({'error': '請提供名片名稱'}), 400
        
        # 解析Flex JSON
        import json
        try:
            flex_data = json.loads(data['flex_json']) if isinstance(data['flex_json'], str) else data['flex_json']
        except json.JSONDecodeError:
            return jsonify({'error': 'Flex JSON格式錯誤'}), 400
        
        # 建立或更新客戶資料
        customer_name = data.get('customer_name', '詠順工程行 鍾師富')
        customer = Customer.query.filter_by(name=customer_name).first()
        
        if not customer:
            customer = Customer(
                name=customer_name,
                company=data.get('company', '詠順工程行'),
                phone='0986372099',  # 從Flex JSON中提取的電話
                line_user_id=data.get('line_user_id', '')
            )
            db.session.add(customer)
            db.session.flush()
        
        # 生成分享URL
        import uuid
        share_id = str(uuid.uuid4())[:8]
        share_url = f"/card/{share_id}"
        
        # 建立已發布名片記錄
        published_card = PublishedCard(
            customer_id=customer.id,
            title=data['card_name'],
            card_data=json.dumps(flex_data, ensure_ascii=False),
            share_url=share_url
        )
        
        db.session.add(published_card)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '名片匯入成功',
            'customer_id': customer.id,
            'card_id': published_card.id,
            'share_url': f"http://localhost:5000{share_url}"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'匯入失敗: {str(e)}'}), 500

@app.route('/api/cards/templates', methods=['GET'])
def get_card_templates():
    """獲取預設名片模板"""
    yongshun_template = {
        "type": "carousel",
        "contents": [
            {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "size": "full",
                    "aspectRatio": "2:3",
                    "aspectMode": "cover",
                    "url": "https://i.pinimg.com/736x/84/0e/9d/840e9dcb12b1e1ba83084d9aa6e6c055.jpg"
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "uri",
                                "label": "分享我的名片",
                                "uri": "https://alterli.pse.is/823k9a"
                            },
                            "color": "#5c8bc3"
                        },
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "uri",
                                "label": "加入 LINE 好友",
                                "uri": "https://line.me/ti/p/4sd0iVha9l"
                            },
                            "color": "#807e7c"
                        }
                    ],
                    "backgroundColor": "#ffffff"
                }
            },
            {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "size": "full",
                    "aspectRatio": "2:3",
                    "aspectMode": "cover",
                    "url": "https://i.pinimg.com/736x/f8/e7/83/f8e7833cbd6a1db6eb72eaaf4b985b8c.jpg"
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "uri",
                                "label": "來電咨詢",
                                "uri": "tel:0986372099"
                            },
                            "color": "#5c8bc3"
                        },
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "uri",
                                "label": "預約抓漏",
                                "uri": "https://page.line.me/R9rnAK"
                            },
                            "color": "#807e7c"
                        }
                    ],
                    "backgroundColor": "#ffffff"
                }
            },
            {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "size": "full",
                    "aspectRatio": "2:3",
                    "aspectMode": "cover",
                    "url": "https://i.pinimg.com/736x/f8/63/e6/f863e676699fc4597b5899a1d9eb7357.jpg"
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "uri",
                                "label": "抓漏日常",
                                "uri": "https://alterli.pse.is/823j7f"
                            },
                            "color": "#5c8bc3"
                        },
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "uri",
                                "label": "抓漏案例",
                                "uri": "https://alterli.pse.is/823j8c"
                            },
                            "color": "#807e7c"
                        }
                    ],
                    "backgroundColor": "#ffffff"
                }
            },
            {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "size": "full",
                    "aspectRatio": "2:3",
                    "aspectMode": "cover",
                    "url": "https://i.pinimg.com/736x/64/b9/c6/64b9c6feb6c09bcd6b1fa9e2e6a0b5c0.jpg"
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "uri",
                                "label": "五星好評",
                                "uri": "https://alterli.pse.is/823jyx"
                            },
                            "color": "#5c8bc3"
                        },
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "uri",
                                "label": "關於鍾師富",
                                "uri": "https://alterli.pse.is/823k3g"
                            },
                            "color": "#807e7c"
                        }
                    ],
                    "backgroundColor": "#ffffff"
                }
            },
            {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "size": "full",
                    "aspectRatio": "2:3",
                    "aspectMode": "cover",
                    "url": "https://i.pinimg.com/736x/b5/c9/0f/b5c90f3cc4f6cdd505ff23167756ca6a.jpg"
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "uri",
                                "label": "如何 AI 抓漏",
                                "uri": "https://alterli.pse.is/823j93"
                            },
                            "color": "#5c8bc3"
                        },
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "uri",
                                "label": "BNI 五表",
                                "uri": "https://alterli.pse.is/823ja7"
                            },
                            "color": "#807e7c"
                        }
                    ],
                    "backgroundColor": "#ffffff"
                }
            }
        ]
    }
    
    templates = [
        {
            'id': 'yongshun_engineering',
            'name': '詠順工程行 - 鍾師富',
            'description': '專業抓漏工程服務，5張輪播式名片',
            'type': 'carousel',
            'preview_image': 'https://i.pinimg.com/736x/84/0e/9d/840e9dcb12b1e1ba83084d9aa6e6c055.jpg',
            'flex_json': yongshun_template
        }
    ]
    
    return jsonify({
        'success': True,
        'templates': templates
    })

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

