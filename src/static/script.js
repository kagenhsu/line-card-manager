// 全域變數
let customers = [];
let selectedCustomers = new Set();
let editingCustomerId = null;

// API 基礎URL
const API_BASE = '/api';

// DOM 元素
const elements = {
    customersContainer: document.getElementById('customersContainer'),
    searchInput: document.getElementById('searchInput'),
    addCustomerBtn: document.getElementById('addCustomerBtn'),
    lineConfigBtn: document.getElementById('lineConfigBtn'),
    batchSendBtn: document.getElementById('batchSendBtn'),
    selectAllBtn: document.getElementById('selectAllBtn'),
    refreshBtn: document.getElementById('refreshBtn'),
    selectedCount: document.getElementById('selectedCount'),
    customerModal: document.getElementById('customerModal'),
    customerForm: document.getElementById('customerForm'),
    modalTitle: document.getElementById('modalTitle'),
    lineConfigModal: document.getElementById('lineConfigModal'),
    lineConfigStatus: document.getElementById('lineConfigStatus'),
    testConnectionBtn: document.getElementById('testConnectionBtn'),
    notification: document.getElementById('notification')
};

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadCustomers();
    checkLineConfig();
});

// 事件監聽器
function initializeEventListeners() {
    // 搜尋功能
    elements.searchInput.addEventListener('input', debounce(handleSearch, 300));
    
    // 按鈕事件
    elements.addCustomerBtn.addEventListener('click', () => openCustomerModal());
    elements.lineConfigBtn.addEventListener('click', () => openLineConfigModal());
    elements.batchSendBtn.addEventListener('click', handleBatchSend);
    elements.selectAllBtn.addEventListener('click', handleSelectAll);
    elements.refreshBtn.addEventListener('click', loadCustomers);
    elements.testConnectionBtn.addEventListener('click', testLineConnection);
    
    // 表單提交
    elements.customerForm.addEventListener('submit', handleCustomerSubmit);
    
    // LINE設定表單提交
    const lineConfigForm = document.getElementById('lineConfigForm');
    if (lineConfigForm) {
        lineConfigForm.addEventListener('submit', handleLineConfigSubmit);
    }
    
    // 模態框關閉
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', closeModals);
    });
    
    // 點擊模態框背景關閉
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModals();
        });
    });
    
    // ESC 鍵關閉模態框
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModals();
    });
}

// 載入客戶資料
async function loadCustomers() {
    try {
        showLoading();
        const response = await fetch(`${API_BASE}/customers`);
        if (!response.ok) throw new Error('載入客戶資料失敗');
        
        customers = await response.json();
        renderCustomers(customers);
        updateSelectedCount();
    } catch (error) {
        console.error('載入客戶資料錯誤:', error);
        showNotification('載入客戶資料失敗', 'error');
        elements.customersContainer.innerHTML = '<div class="loading">載入失敗，請重新整理</div>';
    }
}

// 渲染客戶列表
function renderCustomers(customerList) {
    if (customerList.length === 0) {
        elements.customersContainer.innerHTML = `
            <div class="loading">
                <i class="fas fa-users"></i> 尚無客戶資料，請新增客戶
            </div>
        `;
        return;
    }
    
    const html = customerList.map(customer => {
        const hasCard = customer.has_published_card;
        const cardStatus = hasCard ? '已上架' : '未上架';
        const cardStatusClass = hasCard ? 'status-published' : 'status-unpublished';
        
        return `
        <div class="customer-card" data-customer-id="${customer.id}">
            <input type="checkbox" class="customer-checkbox" 
                   data-customer-id="${customer.id}"
                   ${selectedCustomers.has(customer.id) ? 'checked' : ''}>
            
            <div class="customer-info">
                <div class="customer-main">
                    <div class="customer-name">${escapeHtml(customer.name)}</div>
                    <div class="customer-company">${escapeHtml(customer.company || '未設定公司')}</div>
                    <div class="card-status ${cardStatusClass}">
                        <i class="fas ${hasCard ? 'fa-check-circle' : 'fa-times-circle'}"></i>
                        名片狀態: ${cardStatus}
                    </div>
                </div>
                
                <div class="customer-contact">
                    <div>${escapeHtml(customer.phone || '未設定電話')}</div>
                    <div>${escapeHtml(customer.email || '未設定信箱')}</div>
                </div>
                
                <div class="customer-status">
                    <span class="status-badge ${customer.line_user_id ? 'status-active' : 'status-inactive'}">
                        ${customer.line_user_id ? 'LINE已連結' : 'LINE未連結'}
                    </span>
                    ${customer.contract_end_date ? `<small>合約到期: ${customer.contract_end_date}</small>` : ''}
                </div>
            </div>
            
            <div class="customer-actions">
                ${hasCard ? `
                <button class="btn btn-sm btn-success" onclick="editCard(${customer.id})">
                    <i class="fas fa-paint-brush"></i> 編輯名片
                </button>
                <button class="btn btn-sm btn-info" onclick="viewCard(${customer.id})">
                    <i class="fas fa-eye"></i> 查看名片
                </button>
                ` : `
                <button class="btn btn-sm btn-warning" onclick="createCard(${customer.id})">
                    <i class="fas fa-plus"></i> 建立名片
                </button>
                <button class="btn btn-sm btn-outline" onclick="previewCard(${customer.id})">
                    <i class="fas fa-eye"></i> 預覽
                </button>
                `}
                <button class="btn btn-sm btn-success" onclick="sendCard(${customer.id})" 
                        ${!customer.line_user_id ? 'disabled' : ''}>
                    <i class="fas fa-paper-plane"></i> 發送
                </button>
                <button class="btn btn-sm btn-outline" onclick="editCustomer(${customer.id})">
                    <i class="fas fa-edit"></i> 編輯
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteCustomer(${customer.id})">
                    <i class="fas fa-trash"></i> 刪除
                </button>
            </div>
        </div>
    `;
    }).join('');
    
    elements.customersContainer.innerHTML = html;
    
    // 綁定複選框事件
    document.querySelectorAll('.customer-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', handleCustomerSelect);
    });
}

// 顯示載入中
function showLoading() {
    elements.customersContainer.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i> 載入中...
        </div>
    `;
}

// 搜尋功能
async function handleSearch() {
    const query = elements.searchInput.value.trim();
    
    if (!query) {
        renderCustomers(customers);
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/customers/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('搜尋失敗');
        
        const results = await response.json();
        renderCustomers(results);
    } catch (error) {
        console.error('搜尋錯誤:', error);
        showNotification('搜尋失敗', 'error');
    }
}

// 客戶選擇處理
function handleCustomerSelect(e) {
    const customerId = parseInt(e.target.dataset.customerId);
    
    if (e.target.checked) {
        selectedCustomers.add(customerId);
    } else {
        selectedCustomers.delete(customerId);
    }
    
    updateSelectedCount();
}

// 全選/取消全選
function handleSelectAll() {
    const checkboxes = document.querySelectorAll('.customer-checkbox');
    const allSelected = selectedCustomers.size === checkboxes.length;
    
    if (allSelected) {
        // 取消全選
        selectedCustomers.clear();
        checkboxes.forEach(cb => cb.checked = false);
        elements.selectAllBtn.innerHTML = '<i class="fas fa-check-square"></i> 全選';
    } else {
        // 全選
        checkboxes.forEach(cb => {
            cb.checked = true;
            selectedCustomers.add(parseInt(cb.dataset.customerId));
        });
        elements.selectAllBtn.innerHTML = '<i class="fas fa-square"></i> 取消全選';
    }
    
    updateSelectedCount();
}

// 更新選中數量
function updateSelectedCount() {
    const count = selectedCustomers.size;
    elements.selectedCount.textContent = count;
    elements.batchSendBtn.disabled = count === 0;
    
    // 更新全選按鈕狀態
    const checkboxes = document.querySelectorAll('.customer-checkbox');
    const allSelected = count === checkboxes.length && count > 0;
    elements.selectAllBtn.innerHTML = allSelected ? 
        '<i class="fas fa-square"></i> 取消全選' : 
        '<i class="fas fa-check-square"></i> 全選';
}

// 批量發送
async function handleBatchSend() {
    if (selectedCustomers.size === 0) return;
    
    if (!confirm(`確定要發送電子名片給選中的 ${selectedCustomers.size} 位客戶嗎？`)) {
        return;
    }
    
    try {
        elements.batchSendBtn.disabled = true;
        elements.batchSendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 發送中...';
        
        const response = await fetch(`${API_BASE}/line/send-card-batch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ customer_ids: Array.from(selectedCustomers) })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification(`批量發送完成！成功: ${result.summary.success}, 失敗: ${result.summary.error}`, 'success');
            selectedCustomers.clear();
            updateSelectedCount();
            renderCustomers(customers); // 重新渲染以更新複選框狀態
        } else {
            throw new Error(result.error || '批量發送失敗');
        }
    } catch (error) {
        console.error('批量發送錯誤:', error);
        showNotification(error.message, 'error');
    } finally {
        elements.batchSendBtn.disabled = false;
        elements.batchSendBtn.innerHTML = '<i class="fas fa-paper-plane"></i> 批量發送 (<span id="selectedCount">0</span>)';
        // 重新綁定 selectedCount 元素
        elements.selectedCount = document.getElementById('selectedCount');
        updateSelectedCount();
    }
}

// 開啟客戶模態框
function openCustomerModal(customerId = null) {
    editingCustomerId = customerId;
    
    if (customerId) {
        // 編輯模式
        const customer = customers.find(c => c.id === customerId);
        if (!customer) return;
        
        elements.modalTitle.textContent = '編輯客戶';
        fillCustomerForm(customer);
    } else {
        // 新增模式
        elements.modalTitle.textContent = '新增客戶';
        elements.customerForm.reset();
    }
    
    elements.customerModal.classList.add('show');
}

// 填充客戶表單
function fillCustomerForm(customer) {
    const fields = ['name', 'phone', 'email', 'company', 'position', 'line_user_id', 
                   'address', 'website', 'facebook_url', 'google_map_url', 'notes', 'contract_end_date'];
    
    fields.forEach(field => {
        const element = document.getElementById(`customer${field.charAt(0).toUpperCase() + field.slice(1).replace(/_([a-z])/g, (g) => g[1].toUpperCase())}`);
        if (element) {
            element.value = customer[field] || '';
        }
    });
}

// 處理客戶表單提交
async function handleCustomerSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(elements.customerForm);
    const customerData = Object.fromEntries(formData.entries());
    
    // 清理空值
    Object.keys(customerData).forEach(key => {
        if (!customerData[key]) {
            customerData[key] = null;
        }
    });
    
    try {
        const url = editingCustomerId ? 
            `${API_BASE}/customers/${editingCustomerId}` : 
            `${API_BASE}/customers`;
        
        const method = editingCustomerId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(customerData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification(editingCustomerId ? '客戶資料更新成功' : '客戶新增成功', 'success');
            closeModals();
            loadCustomers();
        } else {
            throw new Error(result.error || '操作失敗');
        }
    } catch (error) {
        console.error('客戶操作錯誤:', error);
        showNotification(error.message, 'error');
    }
}

// 編輯客戶
function editCustomer(customerId) {
    openCustomerModal(customerId);
}

// 刪除客戶
async function deleteCustomer(customerId) {
    const customer = customers.find(c => c.id === customerId);
    if (!customer) return;
    
    if (!confirm(`確定要刪除客戶「${customer.name}」嗎？此操作無法復原。`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/customers/${customerId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('客戶刪除成功', 'success');
            selectedCustomers.delete(customerId);
            loadCustomers();
        } else {
            throw new Error('刪除失敗');
        }
    } catch (error) {
        console.error('刪除客戶錯誤:', error);
        showNotification(error.message, 'error');
    }
}

// 上架名片
async function publishCard(customerId) {
    try {
        const response = await fetch(`${API_BASE}/cards/publish`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ customer_id: customerId })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification(`名片已成功上架！分享連結：${result.share_url}`, 'success');
            
            // 顯示分享連結對話框
            showShareDialog(result.share_url, result.card_id);
        } else {
            throw new Error(result.error || '上架名片失敗');
        }
    } catch (error) {
        console.error('上架名片錯誤:', error);
        showNotification(error.message, 'error');
    }
}

// 顯示分享連結對話框
function showShareDialog(shareUrl, cardId) {
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>名片已成功上架</h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <div class="share-info">
                    <h4>分享連結</h4>
                    <div class="share-url-container">
                        <input type="text" id="shareUrl" value="${shareUrl}" readonly>
                        <button class="btn btn-primary" onclick="copyShareUrl()">複製連結</button>
                    </div>
                    
                    <div class="share-actions">
                        <button class="btn btn-success" onclick="openCard('${shareUrl}')">
                            <i class="fas fa-external-link-alt"></i> 預覽名片
                        </button>
                        <button class="btn btn-info" onclick="shareToLine('${shareUrl}')">
                            <i class="fab fa-line"></i> 分享到LINE
                        </button>
                        <button class="btn btn-secondary" onclick="shareToFacebook('${shareUrl}')">
                            <i class="fab fa-facebook"></i> 分享到Facebook
                        </button>
                    </div>
                    
                    <div class="qr-code-container">
                        <h4>QR Code</h4>
                        <div id="qrcode"></div>
                        <small>掃描QR Code即可查看名片</small>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary modal-close">關閉</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 生成QR Code
    generateQRCode(shareUrl);
    
    // 綁定關閉事件
    modal.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
            document.body.removeChild(modal);
        });
    });
    
    // 點擊背景關閉
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

// 複製分享連結
function copyShareUrl() {
    const shareUrlInput = document.getElementById('shareUrl');
    shareUrlInput.select();
    shareUrlInput.setSelectionRange(0, 99999);
    
    navigator.clipboard.writeText(shareUrlInput.value).then(() => {
        showNotification('分享連結已複製到剪貼簿', 'success');
    }).catch(() => {
        // 備用方法
        document.execCommand('copy');
        showNotification('分享連結已複製到剪貼簿', 'success');
    });
}

// 開啟名片頁面
function openCard(url) {
    window.open(url, '_blank');
}

// 分享到LINE
function shareToLine(url) {
    const lineUrl = `https://social-plugins.line.me/lineit/share?url=${encodeURIComponent(url)}`;
    window.open(lineUrl, '_blank');
}

// 分享到Facebook
function shareToFacebook(url) {
    const fbUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
    window.open(fbUrl, '_blank');
}

// 生成QR Code
function generateQRCode(url) {
    const qrContainer = document.getElementById('qrcode');
    if (qrContainer) {
        // 使用Google Charts API生成QR Code
        const qrUrl = `https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl=${encodeURIComponent(url)}`;
        qrContainer.innerHTML = `<img src="${qrUrl}" alt="QR Code" style="max-width: 200px;">`;
    }
}

// 預覽名片
async function previewCard(customerId) {
    try {
        const response = await fetch(`${API_BASE}/line/preview-card/${customerId}`);
        const result = await response.json();
        
        if (response.ok) {
            // 在新視窗中顯示 Flex Message JSON
            const newWindow = window.open('', '_blank');
            newWindow.document.write(`
                <html>
                    <head>
                        <title>名片預覽 - ${result.customer_name}</title>
                        <style>
                            body { font-family: monospace; padding: 20px; }
                            pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow: auto; }
                        </style>
                    </head>
                    <body>
                        <h2>名片預覽 - ${result.customer_name}</h2>
                        <p>以下是 LINE Flex Message JSON 格式：</p>
                        <pre>${JSON.stringify(result.flex_message, null, 2)}</pre>
                    </body>
                </html>
            `);
        } else {
            throw new Error(result.error || '預覽失敗');
        }
    } catch (error) {
        console.error('預覽名片錯誤:', error);
        showNotification(error.message, 'error');
    }
}

// 發送名片
async function sendCard(customerId) {
    const customer = customers.find(c => c.id === customerId);
    if (!customer) return;
    
    if (!customer.line_user_id) {
        showNotification('客戶沒有設定 LINE User ID', 'error');
        return;
    }
    
    if (!confirm(`確定要發送電子名片給「${customer.name}」嗎？`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/line/send-card/${customerId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification(`電子名片已成功發送給 ${customer.name}`, 'success');
        } else {
            throw new Error(result.error || '發送失敗');
        }
    } catch (error) {
        console.error('發送名片錯誤:', error);
        showNotification(error.message, 'error');
    }
}

// 開啟 LINE 設定模態框
function openLineConfigModal() {
    elements.lineConfigModal.classList.add('show');
    checkLineConfig();
}

// 處理LINE設定表單提交
async function handleLineConfigSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(document.getElementById('lineConfigForm'));
    const configData = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch(`${API_BASE}/line/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(configData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification('LINE設定已成功更新', 'success');
            checkLineConfig(); // 重新檢查設定狀態
        } else {
            throw new Error(result.error || 'LINE設定更新失敗');
        }
    } catch (error) {
        console.error('LINE設定更新錯誤:', error);
        showNotification(error.message, 'error');
    }
}

// 檢查 LINE 設定
async function checkLineConfig() {
    try {
        elements.lineConfigStatus.innerHTML = `
            <div class="loading">
                <i class="fas fa-spinner fa-spin"></i> 檢查設定中...
            </div>
        `;
        
        const response = await fetch(`${API_BASE}/line/config`);
        const result = await response.json();
        
        if (result.has_access_token && result.has_channel_secret) {
            elements.lineConfigStatus.innerHTML = `
                <div class="config-success">
                    <i class="fas fa-check-circle"></i> LINE Bot 設定完成
                    <br><small>Access Token: ${result.access_token_preview}</small>
                    <br><small>Channel Secret: ${result.channel_secret_preview}</small>
                </div>
            `;
            
            // 如果已有設定，載入到表單中（僅顯示預覽）
            const accessTokenField = document.getElementById('accessToken');
            const channelSecretField = document.getElementById('channelSecret');
            if (accessTokenField && channelSecretField) {
                accessTokenField.placeholder = `已設定 (${result.access_token_preview})`;
                channelSecretField.placeholder = `已設定 (${result.channel_secret_preview})`;
            }
        } else {
            elements.lineConfigStatus.innerHTML = `
                <div class="config-error">
                    <i class="fas fa-exclamation-triangle"></i> LINE Bot 設定不完整
                    <br><small>
                        ${!result.has_access_token ? '缺少 Access Token ' : ''}
                        ${!result.has_channel_secret ? '缺少 Channel Secret' : ''}
                    </small>
                </div>
            `;
        }
    } catch (error) {
        console.error('檢查 LINE 設定錯誤:', error);
        elements.lineConfigStatus.innerHTML = `
            <div class="config-error">
                <i class="fas fa-times-circle"></i> 無法檢查 LINE 設定
            </div>
        `;
    }
}

// 測試 LINE 連線
async function testLineConnection() {
    try {
        elements.testConnectionBtn.disabled = true;
        elements.testConnectionBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 測試中...';
        
        const response = await fetch(`${API_BASE}/line/test-connection`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification('LINE API 連線測試成功', 'success');
        } else {
            throw new Error(result.error || '連線測試失敗');
        }
    } catch (error) {
        console.error('LINE 連線測試錯誤:', error);
        showNotification(error.message, 'error');
    } finally {
        elements.testConnectionBtn.disabled = false;
        elements.testConnectionBtn.innerHTML = '測試連線';
    }
}

// 關閉所有模態框
function closeModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.remove('show');
    });
    editingCustomerId = null;
}

// 顯示通知
function showNotification(message, type = 'info') {
    elements.notification.textContent = message;
    elements.notification.className = `notification ${type}`;
    elements.notification.classList.add('show');
    
    setTimeout(() => {
        elements.notification.classList.remove('show');
    }, 5000);
}

// 工具函數
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}



// 建立名片
function createCard(customerId) {
    // 跳轉到專業設計器，並帶上客戶ID參數
    window.location.href = `/flex-card-builder-v2.html?customer_id=${customerId}`;
}

// 編輯名片
function editCard(customerId) {
    // 跳轉到專業設計器，並帶上客戶ID參數進行編輯
    window.location.href = `/flex-card-builder-v2.html?customer_id=${customerId}&mode=edit`;
}

// 查看名片
async function viewCard(customerId) {
    try {
        const response = await fetch(`${API_BASE}/cards/get-by-customer/${customerId}`);
        const result = await response.json();
        
        if (response.ok) {
            // 開啟名片分享連結
            window.open(result.share_url, '_blank');
        } else {
            throw new Error(result.error || '無法取得名片資料');
        }
    } catch (error) {
        console.error('查看名片錯誤:', error);
        showNotification(error.message, 'error');
    }
}

// 更新客戶資料API，加入名片狀態檢查
async function loadCustomers() {
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE}/customers`);
        if (!response.ok) throw new Error('載入客戶資料失敗');
        
        const data = await response.json();
        customers = data;
        
        // 檢查每個客戶的名片狀態
        for (let customer of customers) {
            try {
                const cardResponse = await fetch(`${API_BASE}/cards/get-by-customer/${customer.id}`);
                customer.has_published_card = cardResponse.ok;
            } catch {
                customer.has_published_card = false;
            }
        }
        
        renderCustomers(customers);
    } catch (error) {
        console.error('載入客戶錯誤:', error);
        showNotification('載入客戶資料失敗', 'error');
        elements.customersContainer.innerHTML = `
            <div class="error">
                <i class="fas fa-exclamation-triangle"></i>
                載入失敗，請重新整理頁面
            </div>
        `;
    }
}

