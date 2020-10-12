function sendHeight() {
    const height = document.documentElement.getBoundingClientRect().height;

    parent.postMessage({
        'height': Math.round(height),
        'url': window.location.href
    }, '*');
}

window.addEventListener('load', sendHeight);
window.addEventListener('resize', sendHeight);
