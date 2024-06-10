document.querySelectorAll('pre code').forEach((block) => {
	if (block.classList.length > 0){
		hljs.highlightBlock(block);
	}
	block.classList.add('hljs');
});