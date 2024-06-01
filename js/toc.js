///////////////////////////////////////////////////////////////////////////////////////////////////////////////

/*/////////// 目录侧边栏 ////////////////*/


function makeIds() {
    /* 
        功能：
            为fluid容器中的h类标签添加id
        说明：
            参考tocbot官网
     */


    var content = document.querySelector('.fluid');
    var headings = content.querySelectorAll('h1, h2, h3, h4, h5, h6, h7');
    var headingMap = {};

    Array.prototype.forEach.call(headings, function (heading) {
        var id = heading.id
            ? heading.id
            : encodeURIComponent(heading.innerText.trim().toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, ''));
        headingMap[id] = !isNaN(headingMap[id]) ? ++headingMap[id] : 0;
        if (headingMap[id]) {
            heading.id = id + '-' + headingMap[id];
        } else {
            heading.id = id;
        }
    });
}

makeIds()

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