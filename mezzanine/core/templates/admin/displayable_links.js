var tinyMCELinkList = [
    {% for url, title in links %}
    ['{{ title|escapejs }}', '{{ url|escapejs }}']{% if not forloop.last %},{% endif %}
    {% endfor %}
];
