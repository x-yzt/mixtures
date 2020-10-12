function sendHeight() {
    parent.postMessage({
        'height': document.body.scrollHeight,
        'url': window.location.href
    }, '*');
}

window.addEventListener('load', sendHeight);
window.addEventListener('resize', sendHeight);
