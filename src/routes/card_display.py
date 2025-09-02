from flask import Blueprint, render_template_string
from src.models.published_card import PublishedCard
from src.models.user import db
import json

card_display_bp = Blueprint('card_display', __name__)

@card_display_bp.route('/card/<card_id>')
def view_card(card_id):
    """公開的名片展示頁面"""
    try:
        # 查找名片
        card = PublishedCard.query.filter_by(card_id=card_id, is_active=True).first()
        
        if not card:
            return render_template_string("""
            <!DOCTYPE html>
            <html lang="zh-TW">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>名片不存在</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .error { color: #e74c3c; }
                </style>
            </head>
            <body>
                <h1 class="error">名片不存在或已下架</h1>
                <p>您要查看的名片可能已被移除或連結有誤。</p>
            </body>
            </html>
            """), 404
        
        # 增加瀏覽次數
        card.view_count += 1
        db.session.commit()
        
        # 解析名片資料
        card_data = json.loads(card.card_data)
        customer = card.customer.to_dict()
        
        # 生成名片展示頁面
        html_template = """
        <!DOCTYPE html>
        <html lang="zh-TW">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ customer.name }}的電子名片</title>
            <meta property="og:title" content="{{ customer.name }}的電子名片">
            <meta property="og:description" content="{{ customer.company or '專業服務' }}">
            <meta property="og:type" content="website">
            <meta property="og:url" content="{{ share_url }}">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }
                .card-container {
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    max-width: 400px;
                    width: 100%;
                    overflow: hidden;
                    animation: slideUp 0.6s ease-out;
                }
                @keyframes slideUp {
                    from { opacity: 0; transform: translateY(30px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .card-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }
                .card-header h1 {
                    font-size: 24px;
                    margin-bottom: 5px;
                }
                .card-header p {
                    opacity: 0.9;
                    font-size: 16px;
                }
                .card-body {
                    padding: 30px 20px;
                }
                .contact-item {
                    display: flex;
                    align-items: center;
                    margin-bottom: 20px;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 10px;
                    transition: transform 0.2s;
                    cursor: pointer;
                }
                .contact-item:hover {
                    transform: translateX(5px);
                }
                .contact-icon {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: 15px;
                    font-size: 18px;
                    color: white;
                }
                .phone-icon { background: #27ae60; }
                .email-icon { background: #3498db; }
                .website-icon { background: #e67e22; }
                .facebook-icon { background: #3b5998; }
                .map-icon { background: #e74c3c; }
                .contact-info h3 {
                    font-size: 14px;
                    color: #666;
                    margin-bottom: 5px;
                }
                .contact-info p {
                    font-size: 16px;
                    color: #333;
                    word-break: break-all;
                }
                .action-buttons {
                    padding: 20px;
                    border-top: 1px solid #eee;
                    display: flex;
                    gap: 10px;
                }
                .btn {
                    flex: 1;
                    padding: 12px;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    cursor: pointer;
                    transition: all 0.2s;
                    text-decoration: none;
                    text-align: center;
                    display: inline-block;
                }
                .btn-primary {
                    background: #667eea;
                    color: white;
                }
                .btn-primary:hover {
                    background: #5a6fd8;
                    transform: translateY(-2px);
                }
                .btn-secondary {
                    background: #6c757d;
                    color: white;
                }
                .btn-secondary:hover {
                    background: #5a6268;
                    transform: translateY(-2px);
                }
                .footer {
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 12px;
                }
                @media (max-width: 480px) {
                    .card-container { margin: 10px; }
                    .card-header { padding: 20px 15px; }
                    .card-body { padding: 20px 15px; }
                }
            </style>
        </head>
        <body>
            <div class="card-container">
                <div class="card-header">
                    <h1>{{ customer.name }}</h1>
                    {% if customer.position %}
                    <p>{{ customer.position }}</p>
                    {% endif %}
                    {% if customer.company %}
                    <p>{{ customer.company }}</p>
                    {% endif %}
                </div>
                
                <div class="card-body">
                    {% if customer.phone %}
                    <div class="contact-item" onclick="window.open('tel:{{ customer.phone }}')">
                        <div class="contact-icon phone-icon">📞</div>
                        <div class="contact-info">
                            <h3>電話</h3>
                            <p>{{ customer.phone }}</p>
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if customer.email %}
                    <div class="contact-item" onclick="window.open('mailto:{{ customer.email }}')">
                        <div class="contact-icon email-icon">✉️</div>
                        <div class="contact-info">
                            <h3>電子郵件</h3>
                            <p>{{ customer.email }}</p>
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if customer.website %}
                    <div class="contact-item" onclick="window.open('{{ customer.website }}', '_blank')">
                        <div class="contact-icon website-icon">🌐</div>
                        <div class="contact-info">
                            <h3>官方網站</h3>
                            <p>{{ customer.website }}</p>
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if customer.facebook_url %}
                    <div class="contact-item" onclick="window.open('{{ customer.facebook_url }}', '_blank')">
                        <div class="contact-icon facebook-icon">📘</div>
                        <div class="contact-info">
                            <h3>Facebook</h3>
                            <p>粉絲專頁</p>
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if customer.google_map_url %}
                    <div class="contact-item" onclick="window.open('{{ customer.google_map_url }}', '_blank')">
                        <div class="contact-icon map-icon">📍</div>
                        <div class="contact-info">
                            <h3>地圖位置</h3>
                            <p>點擊查看地圖</p>
                        </div>
                    </div>
                    {% elif customer.address %}
                    <div class="contact-item">
                        <div class="contact-icon map-icon">📍</div>
                        <div class="contact-info">
                            <h3>地址</h3>
                            <p>{{ customer.address }}</p>
                        </div>
                    </div>
                    {% endif %}
                </div>
                
                <div class="action-buttons">
                    <button class="btn btn-primary" onclick="shareCard()">分享名片</button>
                    <button class="btn btn-secondary" onclick="saveContact()">儲存聯絡人</button>
                </div>
                
                <div class="footer">
                    <p>瀏覽次數：{{ view_count }} | 由 LINE電子名片系統 提供</p>
                </div>
            </div>
            
            <script>
                function shareCard() {
                    if (navigator.share) {
                        navigator.share({
                            title: '{{ customer.name }}的電子名片',
                            text: '{{ customer.company or "專業服務" }}',
                            url: window.location.href
                        });
                    } else {
                        // 複製連結到剪貼簿
                        navigator.clipboard.writeText(window.location.href).then(() => {
                            alert('名片連結已複製到剪貼簿！');
                        });
                    }
                }
                
                function saveContact() {
                    // 生成 vCard 格式
                    const vcard = `BEGIN:VCARD
VERSION:3.0
FN:{{ customer.name }}
{% if customer.company %}ORG:{{ customer.company }}{% endif %}
{% if customer.position %}TITLE:{{ customer.position }}{% endif %}
{% if customer.phone %}TEL:{{ customer.phone }}{% endif %}
{% if customer.email %}EMAIL:{{ customer.email }}{% endif %}
{% if customer.website %}URL:{{ customer.website }}{% endif %}
{% if customer.address %}ADR:;;{{ customer.address }};;;;{% endif %}
END:VCARD`;
                    
                    const blob = new Blob([vcard], { type: 'text/vcard' });
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = '{{ customer.name }}.vcf';
                    a.click();
                    window.URL.revokeObjectURL(url);
                }
            </script>
        </body>
        </html>
        """
        
        from jinja2 import Template
        template = Template(html_template)
        
        return template.render(
            customer=customer,
            share_url=card.share_url,
            view_count=card.view_count
        )
        
    except Exception as e:
        return render_template_string("""
        <!DOCTYPE html>
        <html lang="zh-TW">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>載入錯誤</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error { color: #e74c3c; }
            </style>
        </head>
        <body>
            <h1 class="error">載入名片時發生錯誤</h1>
            <p>{{ error }}</p>
        </body>
        </html>
        """, error=str(e)), 500

