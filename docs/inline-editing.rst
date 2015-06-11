===============
In-line Editing
===============

Mezzanine comes with the ability for content authors to edit content
directly within a page while viewing it on the website, rather than having
to log into the admin area. Content authors can simply log into the admin
area as usual, but by selecting *Site* on the login screen the author will
then be redirected back to the website where a small *Edit* icon will be
found next to each piece of editable content, such as a page's title or a
blog post's body. Clicking on the Edit icon will allow the author to update
the individual piece of content without leaving the page.

In-line editing can be disabled by setting ``INLINE_EDITING_ENABLED`` to
``False``.

Template Configuration
======================

Making content in-line editable is as simple as wrapping model
fields with a template tag in your templates. The default templates
installed with Mezzanine all have their content configured to be in-line
editable. When developing your own templates from scratch though, you'll
need to perform this step yourself.

The first step is to ensure you have a the template tag ``editable_loader``
specified right before the closing ``</body>`` tag in each template.
Typically this only needs to be defined in your top-most base template::

    {% load mezzanine_tags %}
    <html>
    <head>
        <title>My Website</title>
    </head>
    <body>
        <!-- Content goes here -->
        {% editable_loader %}
    </body>
    </html>

If your site does not use jQuery, you'll need to include it conditionally in
your template's `<head>` if the user is a staff member. If you're using a
different JS library, you can use `jQuery.noConflict()` to avoid it overwriting
the `$` symbol.

::

    {% if user.is_staff %}
        <script src="{{ STATIC_URL }}mezzanine/js/jquery-1.7.2.min.js">
            jQuery.noConflict();
        </script>
    {% endif %}

The second step is to wrap each instance of a model field with the
``editable`` and ``endeditable`` template tags, with the field specified as
the ``editable`` tag's argument. The content between the two tags is what
will visibly be hinted to the content author as being editable. It's possible to not provide any content between
the two tags, in which case the value for the model field specified for the
``editable`` tag will simply be used. The model field must always be
specified in the format ``instance_name.field_name`` where ``instance_name``
is the name of a model instance in the template context. For example,
suppose we had a ``page`` variable in our template with ``title`` and
``content`` fields::

    {% load mezzanine_tags %}
    <html>
    <head>
        <title>{{ page.title }}</title>
    </head>
    <body>

        <!--
        No content is specified between the editable tags here, so the
        page.title field is simply displayed inside the <h1> tags.
        -->
        <h1>
            {% editable page.title %}{% endeditable %}
        </h1>

        <!--
        Here we are manipulating how the editable content will be regularly
        displayed on the page using Django's truncatewords_html filter as
        well as some in-line markup.
        -->
        <div>
            {% editable page.content %}
            <p style="text-align:justify;">
                {{ page.content|truncatewords_html:50 }}
            </p>
            {% endeditable %}
        </div>

        {% editable_loader %}
    </body>
    </html>

The ``editable`` template tag also allows multiple fields for a model
instance to be given as arguments to a single ``editable`` tag. The
result of this is still a single Edit icon, but when clicked will display
each of the fields specified for editing, grouped together in a single form.
Continuing on from the previous example, if we wanted to group together
the ``title`` and ``content`` fields::

    {% load mezzanine_tags %}
    <html>
    <head>
        <title>{{ page.title }}</title>
    </head>
    <body>

        <!--
        A single Edit icon will be displayed indicating the entire area
        around the h1 and div tags is editable. Clicking it reveals a form
        for editing both fields at once.
        -->
        {% editable page.title page.content %}
        <h1>
            {{ page.title }}
        </h1>
        <div>
            <p style="text-align:justify;">
                {{ page.content|truncatewords_html:50 }}
            </p>
        </div>
        {% endeditable %}

        {% editable_loader %}
    </body>
    </html>

The only caveat to consider with grouping together fields in a single
``editable`` tag is that they must all belong to the same model instance.
