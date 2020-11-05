const origin = "https://mixtures.info";
// const origin = "http://localhost:8000";

window.addEventListener('message', event => {
    if (event.origin === origin) {
        elem = document.querySelector(`iframe[src="${event.data.url}"]`);
        elem.style.height = parseInt(event.data.height) + 'px';
    } else {
        console.warn("Message from untrusted domain", event.origin);
    }
});
