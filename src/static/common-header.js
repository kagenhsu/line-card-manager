// 統一頁首導航JavaScript功能

// 手機版選單切換
function initNavbar() {
    const navbarToggle = document.getElementById('navbarToggle');
    const navbarMenu = document.getElementById('navbarMenu');
    
    if (navbarToggle && navbarMenu) {
        navbarToggle.addEventListener('click', function() {
            navbarMenu.classList.toggle('active');
        });

        // 點擊選單項目後關閉手機版選單
        document.querySelectorAll('.navbar-link').forEach(link => {
            link.addEventListener('click', function() {
                navbarMenu.classList.remove('active');
            });
        });

        // 點擊外部關閉選單
        document.addEventListener('click', function(e) {
            if (!navbarToggle.contains(e.target) && !navbarMenu.contains(e.target)) {
                navbarMenu.classList.remove('active');
            }
        });
    }
}

// 設定當前頁面的活動狀態
function setActiveNavItem(currentPage) {
    const navLinks = document.querySelectorAll('.navbar-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        
        const href = link.getAttribute('href');
        if (href === currentPage || 
            (currentPage === '/' && href === '/') ||
            (currentPage.includes(href) && href !== '/')) {
            link.classList.add('active');
        }
    });
}

// 獲取當前頁面路徑
function getCurrentPage() {
    const path = window.location.pathname;
    const filename = path.split('/').pop();
    
    // 處理不同的頁面路徑
    if (filename === '' || filename === 'index.html') {
        return '/';
    }
    return '/' + filename;
}

// 初始化頁首功能
function initCommonHeader() {
    // 初始化導航功能
    initNavbar();
    
    // 設定當前頁面活動狀態
    const currentPage = getCurrentPage();
    setActiveNavItem(currentPage);
    
    // 添加頁面載入動畫
    document.body.classList.add('page-loaded');
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', initCommonHeader);

// 創建統一的頁首HTML結構
function createCommonHeader(currentPageId = '') {
    return `
        <nav class="main-navbar">
            <div class="navbar-container">
                <a href="/" class="navbar-brand">
                    <i class="fas fa-id-card"></i>
                    LINE電子名片系統
                </a>
                
                <ul class="navbar-menu" id="navbarMenu">
                    <li class="navbar-item">
                        <a href="/" class="navbar-link ${currentPageId === 'home' ? 'active' : ''}">
                            <i class="fas fa-home"></i> 管理後台
                        </a>
                    </li>
                    <li class="navbar-item">
                        <a href="/flex-card-builder-v2.html" class="navbar-link ${currentPageId === 'professional' ? 'active' : ''}">
                            <i class="fas fa-paint-brush"></i> 專業設計器
                        </a>
                    </li>
                    <li class="navbar-item">
                        <a href="/card-gallery.html" class="navbar-link ${currentPageId === 'gallery' ? 'active' : ''}">
                            <i class="fas fa-images"></i> 名片展示廊
                        </a>
                    </li>
                    <li class="navbar-item">
                        <a href="/card-import.html" class="navbar-link ${currentPageId === 'import' ? 'active' : ''}">
                            <i class="fas fa-file-import"></i> 名片匯入
                        </a>
                    </li>
                </ul>
                
                <button class="navbar-toggle" id="navbarToggle">
                    <i class="fas fa-bars"></i>
                </button>
            </div>
        </nav>
    `;
}

// 創建統一的頁面標題結構
function createPageHeader(title, subtitle, icon = 'fas fa-id-card') {
    return `
        <div class="page-header">
            <h1 class="page-title">
                <i class="${icon}"></i>
                ${title}
            </h1>
            <p class="page-subtitle">${subtitle}</p>
        </div>
    `;
}

