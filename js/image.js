// 定义备用路径
// const fallbackBaseUrl = "https://pub-026ecfceb63744219eb65ba54fa5359f.r2.dev/"; // 备用路径

// // 监听所有 .fluid 下的 img 标签
// document.addEventListener('DOMContentLoaded', function() {
//     const images = document.querySelectorAll('div.fluid img, div.profile img');
//     images.forEach(function(img) {
//         img.addEventListener('error', function() {
//             const currentSrc = img.src;

//             // 如果当前已经是备用路径，则移除 src（避免无限循环）
//             if (currentSrc.includes(fallbackBaseUrl)) {
//                 img.removeAttribute('src'); // 仅显示 alt
//                 return;
//             }

//             // 替换主路径为备用路径（保留文件名）
//             const fileName = currentSrc.split('/').pop(); // 提取文件名（如 "test.png"）
//             const newSrc = fallbackBaseUrl + fileName;    // 拼接备用路径
//             img.src = newSrc; // 尝试加载备用图
//         });
//     });
// });


// const img = document.querySelector('img');
// const urls = img.dataset.url.split(';');
// console.log(urls); // ["favicon.ico", "img1.ico", "image1.png"]

// img.src = urls[0];


// ---- 新的图片处理 ----------------------------------------------------------

function loadImagesWithFallback() {
    const images = document.querySelectorAll('img[data-url]');
    
    images.forEach(img => {
        const urls = img.getAttribute('data-url').split(';');
        let currentIndex = 0;
        
        function loadNext() {
            if (currentIndex >= urls.length) {
                console.warn('All image URLs failed to load:', urls);
                return;
            }
            
            const url = urls[currentIndex].trim();
            if (!url) {
                currentIndex++;
                loadNext();
                return;
            }
            
            const testImg = new Image();
            testImg.onload = () => {
                img.src = url;
                img.removeAttribute('data-url');
            };
            testImg.onerror = () => {
                currentIndex++;
                loadNext();
            };
            testImg.src = url;
        }
        
        loadNext();
    });
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', loadImagesWithFallback);

// 如果需要在动态添加图片后也能处理，可以导出这个函数
// window.loadImagesWithFallback = loadImagesWithFallback;