const origin = "https://www.mixtures.info";

window.addEventListener('message', event => {
    if (event.origin === origin) {
        elem = document.querySelector(`iframe[src="${event.data.url}"]`);
        elem.style.height = parseInt(event.data.height) + 30 + 'px';
    }
});
