const ac_data = {
    {% for entry in entries %}
        "{{ entry }}": null,
    {% endfor %}
}