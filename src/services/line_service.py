import requests
import json
import os
from flask import current_app

def get_line_config():
    """取得LINE設定（優先使用檔案設定，其次環境變數）"""
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'line_config.json')
    
    # 嘗試從檔案載入設定
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('access_token') and config.get('channel_secret'):
                    return config
        except:
            pass
    
    # 如果檔案中沒有設定，從應用程式設定或環境變數取得
    return {
        'access_token': current_app.config.get('LINE_CHANNEL_ACCESS_TOKEN', ''),
        'channel_secret': current_app.config.get('LINE_CHANNEL_SECRET', '')
    }

class LineService:
    """LINE Bot API服務類別"""
    
    def __init__(self):
        config = get_line_config()
        self.channel_access_token = config.get('access_token')
        self.api_base_url = 'https://api.line.me/v2/bot'
        
    def send_push_message(self, user_id, messages):
        """發送推播訊息給指定用戶"""
        if not self.channel_access_token:
            raise ValueError("LINE Channel Access Token 未設定")
            
        headers = {
            'Authorization': f'Bearer {self.channel_access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'to': user_id,
            'messages': messages
        }
        
        response = requests.post(
            f'{self.api_base_url}/message/push',
            headers=headers,
            data=json.dumps(data)
        )
        
        if response.status_code != 200:
            raise Exception(f"LINE API錯誤: {response.status_code} - {response.text}")
            
        return response.json() if response.text else {}
    
    def create_business_card_flex_message(self, customer_data):
        """建立電子名片的Flex Message"""
        
        # 基本的電子名片Flex Message模板
        flex_message = {
            "type": "flex",
            "altText": f"{customer_data.get('name', '電子名片')}的電子名片",
            "contents": {
                "type": "bubble",
                "size": "kilo",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "電子名片",
                            "weight": "bold",
                            "size": "sm",
                            "color": "#ffffff"
                        }
                    ],
                    "backgroundColor": "#3C4142",
                    "paddingAll": "15px"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": customer_data.get('name', '姓名'),
                            "weight": "bold",
                            "size": "xl",
                            "color": "#333333"
                        },
                        {
                            "type": "text",
                            "text": customer_data.get('position', '職稱'),
                            "size": "md",
                            "color": "#666666",
                            "margin": "sm"
                        },
                        {
                            "type": "text",
                            "text": customer_data.get('company', '公司名稱'),
                            "size": "md",
                            "color": "#666666",
                            "margin": "sm"
                        },
                        {
                            "type": "separator",
                            "margin": "lg"
                        }
                    ],
                    "spacing": "sm",
                    "paddingAll": "20px"
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": []
                }
            }
        }
        
        # 動態添加聯絡方式按鈕
        footer_contents = []
        
        # 電話按鈕
        if customer_data.get('phone'):
            footer_contents.append({
                "type": "button",
                "style": "primary",
                "height": "sm",
                "action": {
                    "type": "uri",
                    "label": "📞 撥打電話",
                    "uri": f"tel:{customer_data['phone']}"
                }
            })
        
        # 網站按鈕
        if customer_data.get('website'):
            footer_contents.append({
                "type": "button",
                "style": "secondary",
                "height": "sm",
                "action": {
                    "type": "uri",
                    "label": "🌐 官方網站",
                    "uri": customer_data['website']
                },
                "margin": "sm"
            })
        
        # Facebook按鈕
        if customer_data.get('facebook_url'):
            footer_contents.append({
                "type": "button",
                "style": "secondary",
                "height": "sm",
                "action": {
                    "type": "uri",
                    "label": "📘 Facebook",
                    "uri": customer_data['facebook_url']
                },
                "margin": "sm"
            })
        
        # Google地圖按鈕
        if customer_data.get('google_map_url'):
            footer_contents.append({
                "type": "button",
                "style": "secondary",
                "height": "sm",
                "action": {
                    "type": "uri",
                    "label": "📍 地圖位置",
                    "uri": customer_data['google_map_url']
                },
                "margin": "sm"
            })
        
        # 如果有按鈕才加入footer
        if footer_contents:
            flex_message["contents"]["footer"]["contents"] = footer_contents
            flex_message["contents"]["footer"]["spacing"] = "sm"
            flex_message["contents"]["footer"]["paddingAll"] = "20px"
        
        return flex_message
    
    def send_business_card(self, customer):
        """發送電子名片給客戶"""
        if not customer.line_user_id:
            raise ValueError("客戶沒有LINE User ID")
        
        # 建立名片資料
        customer_data = {
            'name': customer.name,
            'position': customer.position,
            'company': customer.company,
            'phone': customer.phone,
            'website': customer.website,
            'facebook_url': customer.facebook_url,
            'google_map_url': customer.google_map_url
        }
        
        # 建立Flex Message
        flex_message = self.create_business_card_flex_message(customer_data)
        
        # 發送訊息
        messages = [flex_message]
        return self.send_push_message(customer.line_user_id, messages)

