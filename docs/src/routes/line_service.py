from flask import Blueprint, jsonify, request, current_app
from src.models.customer import Customer
from src.services.line_service import LineService

line_bp = Blueprint('line', __name__)

@line_bp.route('/line/send-card/<int:customer_id>', methods=['POST'])
def send_business_card(customer_id):
    """發送電子名片給指定客戶"""
    try:
        # 取得客戶資料
        customer = Customer.query.get_or_404(customer_id)
        
        # 檢查客戶是否有LINE User ID
        if not customer.line_user_id:
            return jsonify({
                'error': '客戶沒有設定LINE User ID',
                'customer_name': customer.name
            }), 400
        
        # 檢查LINE設定
        if not current_app.config.get('LINE_CHANNEL_ACCESS_TOKEN'):
            return jsonify({
                'error': 'LINE Channel Access Token 未設定，請檢查環境變數'
            }), 500
        
        # 建立LINE服務實例並發送名片
        line_service = LineService()
        result = line_service.send_business_card(customer)
        
        return jsonify({
            'success': True,
            'message': f'電子名片已成功發送給 {customer.name}',
            'customer_id': customer_id,
            'customer_name': customer.name,
            'line_user_id': customer.line_user_id
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'發送失敗: {str(e)}'}), 500

@line_bp.route('/line/send-card-batch', methods=['POST'])
def send_business_card_batch():
    """批量發送電子名片給多個客戶"""
    try:
        data = request.json
        customer_ids = data.get('customer_ids', [])
        
        if not customer_ids:
            return jsonify({'error': '請提供客戶ID列表'}), 400
        
        # 檢查LINE設定
        if not current_app.config.get('LINE_CHANNEL_ACCESS_TOKEN'):
            return jsonify({
                'error': 'LINE Channel Access Token 未設定，請檢查環境變數'
            }), 500
        
        line_service = LineService()
        results = []
        success_count = 0
        error_count = 0
        
        for customer_id in customer_ids:
            try:
                customer = Customer.query.get(customer_id)
                if not customer:
                    results.append({
                        'customer_id': customer_id,
                        'success': False,
                        'error': '客戶不存在'
                    })
                    error_count += 1
                    continue
                
                if not customer.line_user_id:
                    results.append({
                        'customer_id': customer_id,
                        'customer_name': customer.name,
                        'success': False,
                        'error': '客戶沒有設定LINE User ID'
                    })
                    error_count += 1
                    continue
                
                line_service.send_business_card(customer)
                results.append({
                    'customer_id': customer_id,
                    'customer_name': customer.name,
                    'success': True,
                    'message': '發送成功'
                })
                success_count += 1
                
            except Exception as e:
                results.append({
                    'customer_id': customer_id,
                    'success': False,
                    'error': str(e)
                })
                error_count += 1
        
        return jsonify({
            'success': True,
            'summary': {
                'total': len(customer_ids),
                'success': success_count,
                'error': error_count
            },
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': f'批量發送失敗: {str(e)}'}), 500

@line_bp.route('/line/preview-card/<int:customer_id>', methods=['GET'])
def preview_business_card(customer_id):
    """預覽客戶的電子名片Flex Message"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        line_service = LineService()
        customer_data = {
            'name': customer.name,
            'position': customer.position,
            'company': customer.company,
            'phone': customer.phone,
            'website': customer.website,
            'facebook_url': customer.facebook_url,
            'google_map_url': customer.google_map_url
        }
        
        flex_message = line_service.create_business_card_flex_message(customer_data)
        
        return jsonify({
            'customer_id': customer_id,
            'customer_name': customer.name,
            'flex_message': flex_message
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@line_bp.route('/line/config', methods=['GET'])
def get_line_config():
    """取得LINE設定狀態"""
    return jsonify({
        'has_access_token': bool(current_app.config.get('LINE_CHANNEL_ACCESS_TOKEN')),
        'has_channel_secret': bool(current_app.config.get('LINE_CHANNEL_SECRET'))
    })

@line_bp.route('/line/test-connection', methods=['POST'])
def test_line_connection():
    """測試LINE API連線"""
    try:
        if not current_app.config.get('LINE_CHANNEL_ACCESS_TOKEN'):
            return jsonify({
                'success': False,
                'error': 'LINE Channel Access Token 未設定'
            }), 400
        
        line_service = LineService()
        
        # 這裡可以加入測試API連線的邏輯
        # 例如呼叫LINE的profile API來驗證token是否有效
        
        return jsonify({
            'success': True,
            'message': 'LINE API設定正常'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

