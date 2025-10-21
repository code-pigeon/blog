document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('nav-menu');
    
    hamburger.addEventListener('click', function() {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('show');
    });
    
    // 点击菜单外区域关闭菜单
    document.addEventListener('click', function(event) {
        if (!event.target.closest('nav') && navMenu.classList.contains('show')) {
            hamburger.classList.remove('active');
            navMenu.classList.remove('show');
        }
    });
    
    // 点击菜单项后关闭菜单（移动端）
    navMenu.addEventListener('click', function(event) {
        if (event.target.tagName === 'A' && window.innerWidth <= 768) {
            hamburger.classList.remove('active');
            navMenu.classList.remove('show');
        }
    });
    
    // 窗口大小改变时重置菜单状态
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            hamburger.classList.remove('active');
            navMenu.classList.remove('show');
        }
    });
});