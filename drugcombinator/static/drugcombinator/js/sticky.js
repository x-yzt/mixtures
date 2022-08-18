/*
    This script is an alternative to CSS `position: sticky` which is not very
    convenient when the sticky element is nested in complex positioned layouts.
    
    As soon as an element with the `sticky-anchor` class leaves the viewport,
    its next sibling will be positionned with `position:fixed`.
*/

const stickyObserver = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
        const elem = entry.target.nextElementSibling;

        if (entry.isIntersecting) {
            elem.style.position = 'static';
        } else {
            elem.style.position = 'fixed';
        }
    });
}, { rootMargin: '-64px' });


document.addEventListener('DOMContentLoaded', event => {
    const stickyAnchors = document.querySelectorAll('.sticky-anchor');

    stickyAnchors.forEach(anchor => {
        stickyObserver.observe(anchor);
    });
});
