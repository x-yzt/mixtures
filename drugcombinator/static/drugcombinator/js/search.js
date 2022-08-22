document.addEventListener('DOMContentLoaded', event => {
    const searchBox = document.getElementById('id_q');
    M.Autocomplete.init(searchBox, {data: ac_data});
});
