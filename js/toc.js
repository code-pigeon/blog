///////////////////////////////////////////////////////////////////////////////////////////////////////////////

/*/////////// 目录侧边栏 ////////////////*/
function autoGenerateChineseHeadingIds() {
    /* 
        功能：
            为fluid容器中的h类标签添加id
        说明：
            deepseek生成，支持中文，支持重复标签
    */
    const usedIds = new Set();
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
  
    headings.forEach((heading, index) => {
        if (!heading.id) {
            // 直接使用中文文本，仅做简单清理
            let baseId = heading.textContent.trim()
                .replace(/[^\u4e00-\u9fa5\w\s-]/g, '')  // 保留中文、字母、数字、连字符
                .replace(/\s+/g, '-')      // 空格替换为连字符
                .replace(/-+/g, '-')        // 合并多个连字符
                .replace(/^-+|-+$/g, '');   // 移除开头结尾的连字符

            // 如果生成的ID为空，使用备用方案
            if (!baseId) baseId = `标题-${index + 1}`;

            // 确保ID唯一
            let uniqueId = baseId;
            let counter = 1;
            while (usedIds.has(uniqueId)) {
                uniqueId = `${baseId}-${counter}`;
                counter++;
            }

            heading.id = uniqueId;
            usedIds.add(uniqueId);
        } else {
            usedIds.add(heading.id);
        }
    });
}
autoGenerateChineseHeadingIds();

// ---- 此段代码对Ajax等动态更新网页技术提供支持 ---- 
// ---- 目前不需要 ---- 
/*
// 监听DOM变化
const observer = new MutationObserver(autoGenerateChineseHeadingIds);
observer.observe(document.body, { 
    childList: true, 
    subtree: true 
});

// 初始执行
document.addEventListener('DOMContentLoaded', autoGenerateChineseHeadingIds);
*/
// ---------------------------------------------- 

tocbot.init({
    // Where to render the table of contents.
    tocSelector: '.toc',
    // Where to grab the headings to build the table of contents.
    contentSelector: 'body',
    // Which headings to grab inside of the contentSelector element.
    headingSelector: 'h1, h2, h3',
    // For headings inside relative or absolute positioned containers within content.
    hasInnerContainers: false,
    orderedList: false, // Use unordered list for the table of contents
    scrollSmooth: true // Enable smooth scrolling to headings
});

///////////////////////////////////////////////////////////////////////////////////////////////////////////////

/*/////////// UI优化 ////////////////*/

const toc = document.body.querySelector('.toc');

function toggleTocVisibility() {
    if (window.innerWidth < 1458) {
        if(!toc.classList.contains('toc-hidden')){
          toc.classList.add('toc-hidden');
        }
        return;
    } 

    // if( toc.classList.contains('toc-hidden') ){
    //     toc.classList.remove('toc-hidden');
    // }
}

// Initial check when the page loads
toggleTocVisibility();

// Event listener for the window resize event
window.addEventListener('resize', toggleTocVisibility);


// DOMContentLoaded事件发生之后，就执行下面函数
// DOMContentLoaded事件即html加载完成时，不需要等待css或者图片全部加载完成
window.addEventListener('DOMContentLoaded', event => {

    // Toggle the visibility of the table of contents
    const tocToggle = document.body.querySelector('.toc-toggle');
    const toc = document.body.querySelector('.toc');

    if (tocToggle && toc) {
        // Uncomment Below to persist TOC toggle between refreshes
        if (localStorage.getItem('sb|toc-toggle') === 'true') {
            toc.classList.add('toc-hidden');
        }
        tocToggle.addEventListener('click', event => {
            event.preventDefault();
            toc.classList.toggle('toc-hidden');
            // localStorage.setItem(keylocalStorage.setItem, val)存储一个本地变量，键和值分别为key和val
            // toc.classList.contains('toc-hidden')方法返回一个bool变量，判断toc元素是否属于toc-hidden类
            localStorage.setItem('sb|toc-toggle', toc.classList.contains('toc-hidden'));
        });
    }

});


/* 弃案 */

// function makeIds() {
//     /* 
//         功能：
//             为fluid容器中的h类标签添加id
//         说明：
//             参考tocbot官网
//      */


//     var content = document.querySelector('.fluid');
//     var headings = content.querySelectorAll('h1, h2, h3, h4, h5, h6, h7');
//     var headingMap = {};

//     Array.prototype.forEach.call(headings, function (heading) {
//         var id = heading.id
//             ? heading.id
//             : encodeURIComponent(heading.innerText.trim().toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, ''));
//         headingMap[id] = !isNaN(headingMap[id]) ? ++headingMap[id] : 0;
//         if (headingMap[id]) {
//             heading.id = id + '-' + headingMap[id];
//         } else {
//             heading.id = id;
//         }
//     });
// }

// makeIds()