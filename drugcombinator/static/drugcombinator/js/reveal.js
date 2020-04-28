document.addEventListener('DOMContentLoaded', event => {
    document.querySelectorAll('.draft-modal-reveal').forEach(elem => {
        elem.addEventListener('click', event => {
            elem.parentElement.style.opacity = 0;
            elem.parentElement.style.visibility = 'hidden';
            elem.parentElement.parentElement.classList.remove('hidden');
        });
    });
});