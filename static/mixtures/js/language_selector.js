document.addEventListener('DOMContentLoaded', event => {
    const selector = document.getElementById('lang-selector');
    const dropdown = document.getElementById('lang-dropdown');
    const form = document.getElementById('lang-form');
    const select = form.querySelector('[name="language"]');

    M.Dropdown.init(selector, {
        alignment: 'right',
        coverTrigger: false
    });

    dropdown.querySelectorAll('a').forEach(option => {
        option.addEventListener('click', event => {
            select.value = event.target.getAttribute('data-value');
            form.submit();
        });
    });
});
