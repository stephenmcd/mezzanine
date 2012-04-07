import logging
from django import template
from django.template import loader
from django.db import models
from django.core.cache import cache
from mezzanine.blocks.models import Block

register = template.Library()
logger = logging.getLogger(__name__)

class BasicFlatBlockWrapper(object):
    def prepare(self, parser, token):
        """
        The parser checks for following tag-configurations::

            {% flatblock {block} %}
            {% flatblock {block} {timeout} %}
            {% flatblock {block} using {tpl_name} %}
            {% flatblock {block} {timeout} using {tpl_name} %}
        """
        tokens = token.split_contents()
        self.is_variable = False
        self.tpl_is_variable = False
        self.slug = None
        self.cache_time = 0
        self.tpl_name = None
        tag_name, self.slug, args = tokens[0], tokens[1], tokens[2:]
        num_args = len(args)
        if num_args == 0:
            # Only the block name was specified
            pass
        elif num_args == 1:
            # block and timeout
            self.cache_time = args[0]
            pass
        elif num_args == 2:
            # block, "using", tpl_name
            self.tpl_name = args[1]
        elif num_args == 3:
            # block, timeout, "using", tpl_name
            self.cache_time = args[0]
            self.tpl_name = args[2]
        else:
            raise template.TemplateSyntaxError, "%r tag should have between 1 and 4 arguments" % (tokens[0],)
        # Check to see if the slug is properly double/single quoted
        if not (self.slug[0] == self.slug[-1] and self.slug[0] in ('"', "'")):
            self.is_variable = True
        else:
            self.slug = self.slug[1:-1]
        # Clean up the template name
        if self.tpl_name is not None:
            if not(self.tpl_name[0] == self.tpl_name[-1] and self.tpl_name[0] in ('"', "'")):
                self.tpl_is_variable = True
            else:
                self.tpl_name = self.tpl_name[1:-1]
        if self.cache_time is not None and self.cache_time != 'None':
            self.cache_time = int(self.cache_time)

    def __call__(self, parser, token):
        self.prepare(parser, token)
        return FlatBlockNode(self.slug, self.is_variable, self.cache_time,
                template_name=self.tpl_name,
                tpl_is_variable=self.tpl_is_variable)

class PlainFlatBlockWrapper(BasicFlatBlockWrapper):
    def __call__(self, parser, token):
        self.prepare(parser, token)
        return FlatBlockNode(self.slug, self.is_variable, self.cache_time, False)

do_get_flatblock = BasicFlatBlockWrapper()
do_plain_flatblock = PlainFlatBlockWrapper()

class FlatBlockNode(template.Node):
    def __init__(self, slug, is_variable, cache_time=0, with_template=True,
            template_name=None, tpl_is_variable=False):
        if template_name is None:
            self.template_name = 'blocks/block.html'
        else:
            if tpl_is_variable:
                self.template_name = template.Variable(template_name)
            else:
                self.template_name = template_name
        self.slug = slug
        self.is_variable = is_variable
        self.cache_time = cache_time
        self.with_template = with_template

    def render(self, context):
        if self.is_variable:
            real_slug = template.Variable(self.slug).resolve(context)
        else:
            real_slug = self.slug
        if isinstance(self.template_name, template.Variable):
            real_template = self.template_name.resolve(context)
        else:
            real_template = self.template_name
        # Eventually we want to pass the whole context to the template so that
        # users have the maximum of flexibility of what to do in there.
        if self.with_template:
            new_ctx = template.Context({})
            new_ctx.update(context)
        try:
            flatblock = None
            if self.cache_time != 0:
                cache_key = 'block_' + real_slug
                flatblock = cache.get(cache_key)
            if flatblock is None:

                # if flatblock's slug is hard-coded in template then it is
                # safe and convenient to auto-create block if it doesn't exist.
                # This behaviour can be configured using the
                # FLATBLOCKS_AUTOCREATE_STATIC_BLOCKS setting
                if self.is_variable:
                    flatblock = Block.objects.get(slug=real_slug)
                else:
                    flatblock, _ = Block.objects.get_or_create(
                                      slug=real_slug,
                                      defaults = {'content': real_slug}
                                   )
                if self.cache_time != 0:
                    if self.cache_time is None or self.cache_time == 'None':
                        logger.debug("Caching %s for the cache's default timeout"
                                % (real_slug,))
                        cache.set(cache_key, flatblock)
                    else:
                        logger.debug("Caching %s for %s seconds" % (real_slug,
                            str(self.cache_time)))
                        cache.set(cache_key, flatblock, int(self.cache_time))
                else:
                    logger.debug("Don't cache %s" % (real_slug,))

            if self.with_template:
                tmpl = loader.get_template(real_template)
                new_ctx.update({'flatblock':flatblock})
                return tmpl.render(new_ctx)
            else:
                return flatblock.content
        except Block.DoesNotExist:
            return ''

register.tag('flatblock', do_get_flatblock)
register.tag('plain_flatblock', do_plain_flatblock)
