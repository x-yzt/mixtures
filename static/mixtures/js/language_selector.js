document.addEventListener('DOMContentLoaded', event => {
    // Those are the "GUI" selectors element on the page, it is possible
    // there is multiple of them on a single page
    const selectors = document.querySelectorAll('.lang-selector');
    const dropdowns = document.querySelectorAll('.lang-dropdown');
    // This is the unique, hidden language form that will be used to
    // submit POST data
    const form = document.getElementById('lang-form');
    const select = form.querySelector('[name="language"]');

    selectors.forEach(selector => {
        M.Dropdown.init(selector, {
            alignment: 'right',
            coverTrigger: false
        });
    });

    dropdowns.forEach(dropdown => {
        dropdown.querySelectorAll('a').forEach(option => {
            option.addEventListener('click', event => {
                event.preventDefault();
                select.value = event.target.getAttribute('data-value');
                form.submit();
            });
        });
    });
});
