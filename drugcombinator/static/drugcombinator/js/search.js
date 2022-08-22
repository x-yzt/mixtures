document.addEventListener('DOMContentLoaded', event => {
    const searchBox = document.getElementById('id_q');

    fetch('/autocomplete/')
    .then(response => response.json())
    .then(data => {
        M.Autocomplete.init(searchBox, { data: data });
    });
});
