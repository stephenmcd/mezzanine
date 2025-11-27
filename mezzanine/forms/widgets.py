from django.forms import Widget


class TitleWidget(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return f'<h3 class="form-title">{value}</h3>'
