from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import sys
import time

# 添加 src 目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# 資料庫設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

db = SQLAlchemy(app)

# 確保資料庫目錄存在
os.makedirs(os.path.join(os.path.dirname(__file__), 'database'), exist_ok=True)

# 匯入模型 - 注意順序很重要！
from models.user import User
from models.customer import Customer
from models.card_template import CardTemplate

# 建立基本資料表
with app.app_context():
    db.create_all()

# 匯入有外鍵關聯的模型
from models.published_card import PublishedCard

# 再次建立所有資料表（包含外鍵關聯）
with app.app_context():
    db.create_all()

# 匯入路由
from routes.user import user_bp
from routes.customer import customer_bp
from routes.line_service import line_service_bp
from routes.line_config import line_config_bp
from routes.card_publisher import card_publisher_bp
from routes.card_display import card_display_bp

# 註冊藍圖
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(customer_bp, url_prefix='/api')
app.register_blueprint(line_service_bp, url_prefix='/api')
app.register_blueprint(line_config_bp, url_prefix='/api')
app.register_blueprint(card_publisher_bp, url_prefix='/api')
app.register_blueprint(card_display_bp)

# 健康檢查API
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'LINE電子名片管理系統運行正常',
        'timestamp': time.time()
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

