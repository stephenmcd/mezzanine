===============
In-line Editing
===============

Mezzanine comes with the ability for content authors to edit content 
directly within a page while viewing it on the website, rather than having 
to log into the admin area. Content authors can simply log into the admin 
area as usual, but by selecting *Site* on the login screen the author will 
then be redirected back to the website where a small *Edit* icon will be 
found next to each piece of editable content, such as a page's title or a 
blog post's introduction text. Clicking on the Edit icon will allow the 
author to update the individual piece of content withouth leaving the page.

Template Configuration
======================

Making content in-line editable is mostly as simple as wrapping model 
fields with a template tag within your templates. The default templates 
installed with Mezzanine have all their content configured to be in-line 
editable, but when developing your own templates you'll need to perform 
this step. 

The first step is to ensure you have a single template tag 
``editable_loader`` inside the HTML ``<head>`` tags for every template. 
Typically this would only need to be defined in your top-most base template::

    <html>
    <head>
        <title>My Website</title>
    </head>
    <body>
        <!-- Content goes here -->
    </body>
    </html>
    
The second step is to wrap each instance of a model field with the 
``editable`` and ``endeditable`` template tags. The ``editable`` tag takes 
a single argument which is the model field to be edited. The content 
between the two tags is what will be visibly indicated to the content 
author as being editable. It's possible to not provide any content between 
the two tags, in which case the model field specified for the ``editable`` 
tag will simply be used. The model field must always be specified in the 
format ``instance_name.field_name`` where ``instance_name`` is the name of 
a model instance in the template context. For example, suppose we had a 
``page`` variable in our template with ``title`` and ``content`` fields::

    {% load mezzanine_tags %}
    <html>
    <head>
        <title>{{ page.title }}</title>
        {% editable_loader %}
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
            </P>
            {% endeditable %}
        </div>

    </body>
    </html>

