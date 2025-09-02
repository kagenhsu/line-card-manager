from flask import Blueprint, request, jsonify
import json
from datetime import datetime
from ..models.customer import Customer
from ..models.published_card import PublishedCard
from .. import db

card_import_bp = Blueprint('card_import', __name__)

@card_import_bp.route('/api/cards/import', methods=['POST'])
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
        try:
            flex_data = json.loads(data['flex_json']) if isinstance(data['flex_json'], str) else data['flex_json']
        except json.JSONDecodeError:
            return jsonify({'error': 'Flex JSON格式錯誤'}), 400
        
        # 從Flex JSON中提取資訊
        card_info = extract_card_info(flex_data)
        
        # 建立或更新客戶資料
        customer_data = {
            'name': data.get('customer_name', card_info.get('name', '未知客戶')),
            'company': data.get('company', card_info.get('company', '')),
            'phone': card_info.get('phone', ''),
            'email': card_info.get('email', ''),
            'website': card_info.get('website', ''),
            'facebook': card_info.get('facebook', ''),
            'address': card_info.get('address', ''),
            'line_user_id': data.get('line_user_id', '')
        }
        
        # 檢查是否已存在客戶
        existing_customer = Customer.query.filter_by(name=customer_data['name']).first()
        if existing_customer:
            customer = existing_customer
            # 更新客戶資訊
            for key, value in customer_data.items():
                if value:  # 只更新非空值
                    setattr(customer, key, value)
        else:
            customer = Customer(**customer_data)
            db.session.add(customer)
            db.session.flush()  # 獲取customer.id
        
        # 建立已發布名片記錄
        published_card = PublishedCard(
            customer_id=customer.id,
            card_name=data['card_name'],
            flex_message=json.dumps(flex_data, ensure_ascii=False),
            card_type='carousel' if flex_data.get('type') == 'carousel' else 'bubble',
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(published_card)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '名片匯入成功',
            'customer_id': customer.id,
            'card_id': published_card.id,
            'card_info': card_info
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'匯入失敗: {str(e)}'}), 500

@card_import_bp.route('/api/cards/parse-flex', methods=['POST'])
def parse_flex_json():
    """解析Flex JSON並提取資訊"""
    try:
        data = request.get_json()
        
        if not data.get('flex_json'):
            return jsonify({'error': '請提供Flex Message JSON'}), 400
        
        # 解析Flex JSON
        try:
            flex_data = json.loads(data['flex_json']) if isinstance(data['flex_json'], str) else data['flex_json']
        except json.JSONDecodeError:
            return jsonify({'error': 'Flex JSON格式錯誤'}), 400
        
        # 提取名片資訊
        card_info = extract_card_info(flex_data)
        
        return jsonify({
            'success': True,
            'card_info': card_info,
            'card_type': flex_data.get('type', 'bubble'),
            'cards_count': len(flex_data.get('contents', [])) if flex_data.get('type') == 'carousel' else 1
        })
        
    except Exception as e:
        return jsonify({'error': f'解析失敗: {str(e)}'}), 500

def extract_card_info(flex_data):
    """從Flex Message中提取名片資訊"""
    info = {
        'name': '',
        'company': '',
        'phone': '',
        'email': '',
        'website': '',
        'facebook': '',
        'address': '',
        'images': [],
        'buttons': []
    }
    
    try:
        # 處理Carousel類型
        if flex_data.get('type') == 'carousel':
            contents = flex_data.get('contents', [])
            
            for i, bubble in enumerate(contents):
                card_info = {
                    'card_index': i + 1,
                    'image_url': '',
                    'buttons': []
                }
                
                # 提取圖片
                if bubble.get('hero', {}).get('url'):
                    card_info['image_url'] = bubble['hero']['url']
                    info['images'].append(bubble['hero']['url'])
                
                # 提取按鈕資訊
                footer = bubble.get('footer', {})
                if footer.get('contents'):
                    for button in footer['contents']:
                        if button.get('type') == 'button':
                            button_info = {
                                'label': button.get('action', {}).get('label', ''),
                                'uri': button.get('action', {}).get('uri', ''),
                                'color': button.get('color', ''),
                                'type': button.get('action', {}).get('type', '')
                            }
                            card_info['buttons'].append(button_info)
                            
                            # 嘗試從按鈕中提取聯絡資訊
                            uri = button_info['uri']
                            if uri.startswith('tel:'):
                                info['phone'] = uri.replace('tel:', '')
                            elif uri.startswith('mailto:'):
                                info['email'] = uri.replace('mailto:', '')
                            elif 'facebook.com' in uri:
                                info['facebook'] = uri
                            elif uri.startswith('http'):
                                info['website'] = uri
                
                info['buttons'].append(card_info)
        
        # 處理單一Bubble類型
        elif flex_data.get('type') == 'bubble':
            # 提取圖片
            if flex_data.get('hero', {}).get('url'):
                info['images'].append(flex_data['hero']['url'])
            
            # 提取按鈕資訊
            footer = flex_data.get('footer', {})
            if footer.get('contents'):
                for button in footer['contents']:
                    if button.get('type') == 'button':
                        button_info = {
                            'label': button.get('action', {}).get('label', ''),
                            'uri': button.get('action', {}).get('uri', ''),
                            'color': button.get('color', ''),
                            'type': button.get('action', {}).get('type', '')
                        }
                        info['buttons'].append(button_info)
                        
                        # 提取聯絡資訊
                        uri = button_info['uri']
                        if uri.startswith('tel:'):
                            info['phone'] = uri.replace('tel:', '')
                        elif uri.startswith('mailto:'):
                            info['email'] = uri.replace('mailto:', '')
                        elif 'facebook.com' in uri:
                            info['facebook'] = uri
                        elif uri.startswith('http'):
                            info['website'] = uri
    
    except Exception as e:
        print(f"提取名片資訊時發生錯誤: {e}")
    
    return info

@card_import_bp.route('/api/cards/templates', methods=['GET'])
def get_card_templates():
    """獲取預設名片模板"""
    templates = [
        {
            'id': 'yongshun_engineering',
            'name': '詠順工程行 - 鍾師富',
            'description': '專業抓漏工程服務，5張輪播式名片',
            'type': 'carousel',
            'preview_image': 'https://i.pinimg.com/736x/84/0e/9d/840e9dcb12b1e1ba83084d9aa6e6c055.jpg',
            'flex_json': {
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
        }
    ]
    
    return jsonify({
        'success': True,
        'templates': templates
    })

