function observeElementCreation(targetId, containerSelector = null) {
    // 如果有指定容器，优先使用容器；否则监听整个body
    const observeTarget = containerSelector ? 
        document.querySelector(containerSelector) : document.body;
    
    if (!observeTarget) {
        console.warn(`容器 ${containerSelector} 不存在`);
        return;
    }
    
    const observer = new MutationObserver(function(mutations) {
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({ behavior: 'smooth' });
            console.log(`检测到元素 ${targetId} 已创建，已滚动到该位置`);
            highlightElement(targetElement);
            observer.disconnect();
        }
    });
    
    // 只监听指定容器的变化，大幅减少监听范围
    observer.observe(observeTarget, {
        childList: true,
        subtree: true
    });
    
    // 设置超时
    setTimeout(() => {
        observer.disconnect(); // 直接断开，不需要再次检查元素
        console.log(`监听元素 ${targetId} 超时`);
    }, 2400);
}

// 高亮元素函数
function highlightElement(element) {
    // 保存原始样式
    const originalBackgroundColor = element.style.backgroundColor;
    const originalBoxShadow = element.style.boxShadow;
    const originalTransition = element.style.transition;
    
    // 添加高亮样式
    element.style.transition = 'all 0.5s ease-in-out';
    // element.style.backgroundColor = '#ffffff'; // 浅黄色背景
    element.style.boxShadow = '0 0 10px #62bfff'; // 发光效果
    
    // 3秒后恢复原始样式
    setTimeout(() => {
        element.style.backgroundColor = originalBackgroundColor;
        element.style.boxShadow = originalBoxShadow;
        
        // 再过0.5秒后恢复transition
        setTimeout(() => {
            element.style.transition = originalTransition;
        }, 500);
        
    }, 1800);
}

document.addEventListener('DOMContentLoaded', function() {
    const hash = window.location.hash.substring(1);
    
    if (hash) {
        // 立即检查元素是否存在
        const element = document.getElementById(hash);
        if (element) {
            // 元素已存在，浏览器会自动处理或我们可以立即滚动
            // setTimeout(() => {
            //     element.scrollIntoView({ behavior: 'smooth' });
            // }, 100);
        } else {
            // 元素不存在，开始监听
            console.log(`元素 ${hash} 尚未加载，等待创建...`);
            observeElementCreation(hash, "#vcomments");
        }
    }
    
});