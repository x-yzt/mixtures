document.addEventListener('DOMContentLoaded', event => {
    const searchBox = document.getElementById('id_name_field');
    M.Autocomplete.init(searchBox, {data: ac_data});
});