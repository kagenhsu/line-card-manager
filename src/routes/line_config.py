from flask import Blueprint, request, jsonify, current_app
import os
import json

line_config_bp = Blueprint('line_config', __name__)

# 設定檔案路徑
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'line_config.json')

def ensure_config_dir():
    """確保設定目錄存在"""
    config_dir = os.path.dirname(CONFIG_FILE)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

def load_line_config():
    """載入LINE設定"""
    ensure_config_dir()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_line_config(config):
    """儲存LINE設定"""
    ensure_config_dir()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def get_line_config():
    """取得LINE設定（優先使用檔案設定，其次環境變數）"""
    config = load_line_config()
    
    # 如果檔案中沒有設定，嘗試從環境變數取得
    if not config.get('access_token'):
        config['access_token'] = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
    if not config.get('channel_secret'):
        config['channel_secret'] = os.getenv('LINE_CHANNEL_SECRET', '')
    
    return config

@line_config_bp.route('/line/config', methods=['GET'])
def get_config():
    """取得LINE設定狀態"""
    config = get_line_config()
    
    return jsonify({
        'has_access_token': bool(config.get('access_token')),
        'has_channel_secret': bool(config.get('channel_secret')),
        'access_token_preview': config.get('access_token', '')[:10] + '...' if config.get('access_token') else '',
        'channel_secret_preview': config.get('channel_secret', '')[:10] + '...' if config.get('channel_secret') else ''
    })

@line_config_bp.route('/line/config', methods=['POST'])
def update_config():
    """更新LINE設定"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '無效的請求資料'}), 400
        
        access_token = data.get('access_token', '').strip()
        channel_secret = data.get('channel_secret', '').strip()
        
        if not access_token or not channel_secret:
            return jsonify({'error': 'Access Token 和 Channel Secret 都是必填項目'}), 400
        
        # 基本格式驗證
        if not access_token.startswith(('Bearer ', 'Bot ')):
            # 如果沒有前綴，自動加上
            access_token = access_token
        
        if len(channel_secret) < 10:
            return jsonify({'error': 'Channel Secret 格式不正確'}), 400
        
        # 儲存設定
        config = {
            'access_token': access_token,
            'channel_secret': channel_secret
        }
        save_line_config(config)
        
        # 更新應用程式設定
        current_app.config['LINE_CHANNEL_ACCESS_TOKEN'] = access_token
        current_app.config['LINE_CHANNEL_SECRET'] = channel_secret
        
        return jsonify({
            'success': True,
            'message': 'LINE設定已成功更新'
        })
        
    except Exception as e:
        return jsonify({'error': f'設定更新失敗: {str(e)}'}), 500

@line_config_bp.route('/line/test-connection', methods=['POST'])
def test_connection():
    """測試LINE API連線"""
    try:
        import requests
        
        config = get_line_config()
        access_token = config.get('access_token')
        
        if not access_token:
            return jsonify({'error': 'Access Token 未設定'}), 400
        
        # 測試API連線
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # 使用 LINE Bot Info API 測試連線
        response = requests.get(
            'https://api.line.me/v2/bot/info',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            bot_info = response.json()
            return jsonify({
                'success': True,
                'message': 'LINE API 連線測試成功',
                'bot_info': {
                    'displayName': bot_info.get('displayName', ''),
                    'userId': bot_info.get('userId', ''),
                    'basicId': bot_info.get('basicId', '')
                }
            })
        else:
            return jsonify({
                'error': f'LINE API 連線失敗: HTTP {response.status_code}'
            }), 400
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'LINE API 連線逾時'}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'LINE API 連線錯誤: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'測試連線失敗: {str(e)}'}), 500

