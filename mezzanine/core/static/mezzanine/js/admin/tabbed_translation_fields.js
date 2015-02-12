/*jslint white: true, onevar: true, undef: true, nomen: true, eqeqeq: true,
  plusplus: true, bitwise: true, regexp: true, newcap: true, immed: true */
var google, django, gettext;

(function () {
    var jQuery = window.jQuery || $ || django.jQuery;

    /* Add a new selector to jQuery that excludes parent items which match a given selector */
    jQuery.expr[':'].parents = function(a, i, m) {
        return jQuery(a).parents(m[3]).length < 1;
    };

    jQuery(function ($) {
        var TranslationField = function (options) {
            this.el = options.el;
            this.cls = options.cls;
            this.id = '';
            this.origFieldname = '';
            this.lang = '';
            this.groupId = '';

            this.init = function () {
                var clsBits = this.cls.substring(
                    TranslationField.cssPrefix.length, this.cls.length).split('-');
                this.origFieldname = clsBits[0];
                this.lang = clsBits[1];
                this.id = $(this.el).attr('id');
                this.groupId = this.buildGroupId();
            };

            this.buildGroupId = function () {
                /**
                 * Returns a unique group identifier with respect to the admin's way
                 * of handling inline field name attributes. Essentially that's the
                 * translation field id without the language prefix.
                 *
                 * Examples ('id parameter': 'return value'):
                 *
                 *  'id_name_de':
                 *      'id_name'
                 *  'id_name_zh_tw':
                 *      'id_name'
                 *  'id_name_set-2-name_de':
                 *      'id_name_set-2-name'
                 *  'id_name_set-2-name_zh_tw':
                 *      'id_name_set-2-name'
                 *  'id_name_set-2-0-name_de':
                 *      'id_name_set-2-0-name'
                 *  'id_name_set-2-0-name_zh_tw':
                 *      'id_name_set-2-0-name'
                 *  'id_news-data2-content_type-object_id-0-name_de':
                 *      'id_news-data2-content_type-object_id-0-name'
                 *  'id_news-data2-content_type-object_id-0-name_zh_cn':
                 *      id_news-data2-content_type-object_id-0-name'
                 *  'id_news-data2-content_type-object_id-0-1-name_de':
                 *      'id_news-data2-content_type-object_id-0-1-name'
                 *  'id_news-data2-content_type-object_id-0-1-name_zh_cn':
                 *      id_news-data2-content_type-object_id-0-1-name'
                 */
                // TODO: We should be able to simplify this, the modeltranslation specific
                // field classes are already build to be easily splitable, so we could use them
                // to slice off the language code.
                var idBits = this.id.split('-'),
                    idPrefix = 'id_' + this.origFieldname;
                if (idBits.length === 3) {
                    // Handle standard inlines
                    idPrefix = idBits[0] + '-' + idBits[1] + '-' + idPrefix;
                } else if (idBits.length === 4) {
                    // Handle standard inlines with model used by inline more than once
                    idPrefix = idBits[0] + '-' + idBits[1] + '-' + idBits[2] + '-' + idPrefix;
                } else if (idBits.length === 5 && idBits[3] != '__prefix__') {
                    // Handle nested inlines (https://github.com/Soaa-/django-nested-inlines)
                    idPrefix = idBits[0] + '-' + idBits[1] + '-' + idBits[2] + '-' + idBits[3] + '-' + this.origFieldname;
                } else if (idBits.length === 6) {
                    // Handle generic inlines
                    idPrefix = idBits[0] + '-' + idBits[1] + '-' + idBits[2] + '-' +
                        idBits[3] + '-' + idBits[4] + '-' + this.origFieldname;
                } else if (idBits.length === 7) {
                    // Handle generic inlines with model used by inline more than once
                    idPrefix = idBits[0] + '-' + idBits[1] + '-' + idBits[2] + '-' +
                        idBits[3] + '-' + idBits[4] + '-' + idBits[5] + '-' + this.origFieldname;
                }
                return idPrefix;
            };

            this.init();
        };
        TranslationField.cssPrefix = 'mt-field-';

        var TranslationFieldGrouper = function (options) {
            this.$fields = options.$fields;
            this.groupedTranslations = {};

            this.init = function () {
                // Handle fields inside collapsed groups as added by zinnia
                this.$fields = this.$fields.add('fieldset.collapse-closed .mt');

                this.groupedTranslations = this.getGroupedTranslations();
            };

            this.getGroupedTranslations = function () {
                /**
                 * Returns a grouped set of all model translation fields.
                 * The returned datastructure will look something like this:
                 *
                 * {
                 *     'id_name': {
                 *         'en': HTMLInputElement,
                 *         'de': HTMLInputElement,
                 *         'zh_tw': HTMLInputElement
                 *     },
                 *     'id_name_set-2-name': {
                 *         'en': HTMLTextAreaElement,
                 *         'de': HTMLTextAreaElement,
                 *         'zh_tw': HTMLTextAreaElement
                 *     },
                 *     'id_news-data2-content_type-object_id-0-name': {
                 *         'en': HTMLTextAreaElement,
                 *         'de': HTMLTextAreaElement,
                 *         'zh_tw': HTMLTextAreaElement
                 *     }
                 * }
                 *
                 * The keys are unique group identifiers as returned by
                 * TranslationField.buildGroupId() to handle inlines properly.
                 */
                var self = this,
                    cssPrefix = TranslationField.cssPrefix;
                this.$fields.each(function (idx, el) {
                    $.each($(el).attr('class').split(' '), function(idx, cls) {
                        if (cls.substring(0, cssPrefix.length) === cssPrefix) {
                            var tfield = new TranslationField({el: el, cls: cls});
                            if (!self.groupedTranslations[tfield.groupId]) {
                                self.groupedTranslations[tfield.groupId] = {};
                            }
                            self.groupedTranslations[tfield.groupId][tfield.lang] = el;
                        }
                    });
                });
                return this.groupedTranslations;
            };

            this.init();
        };

        var TabularInlineGroup = function (options) {
            this.$el = options.el;
            this.$table = null;
            this.translationColumns = [];

            this.init = function () {
                this.$table = this.$el.find('.items');
            };

            this.getAllGroupedTranslations = function () {
                var grouper = new TranslationFieldGrouper({
                    $fields: this.$table.find('.mt').filter(
                        'input:visible, textarea:visible, select:visible')
                });
                this.initTable();
                return grouper.groupedTranslations;
            };

            this.getGroupedTranslations = function ($fields) {
                var grouper = new TranslationFieldGrouper({
                    $fields: $fields
                });
                return grouper.groupedTranslations;
            };

            this.initTable = function () {
                var self = this;
                // The table header requires special treatment. In case an inline
                // is declared with extra=0, the translation fields are not visible.
                var thGrouper = new TranslationFieldGrouper({
                    $fields: this.$table.find('.mt').filter('input, textarea, select')
                });
                this.translationColumns = this.getTranslationColumns(thGrouper.groupedTranslations);

                this.$table.find('.legend .form-cell').each(function (idx) {
                    // Hide table heads from which translation fields have been moved out.
                    if($.inArray(idx + 1, self.translationColumns) !== -1) {
                        // FIXME: Why does this break when we use remove instead of hide?
                        $(this).hide();
                    }

                    // Remove language and brackets from table header,
                    // they are displayed in the tab already.
                    if ($(this).html() && $.inArray(idx + 1, self.translationColumns) === -1) {
                        $(this).html($(this).html().replace(/ \[.+\]/, ''));
                    }
                });
            };

            this.getTranslationColumns = function (groupedTranslations) {
                var translationColumns = [];
                // Get table column indexes which have translation fields, but omit the first
                // one per group, because that's where we insert our tab container.
                $.each(groupedTranslations, function (groupId, lang) {
                    var i = 0;
                    $.each(lang, function (lang, el) {
                        var column = $(el).closest('.form-cell').prevAll().length;
                        if (i > 0 && $.inArray(column, translationColumns) === -1) {
                            translationColumns.push(column);
                        }
                        i += 1;
                    });
                });
                return translationColumns;
            };

            this.init();
        };

        function activateFields(groupedTranslations, activeLanguage, containerClass) {
            $.each(groupedTranslations, function (groupId, lang) {
                var activeField = null,
                    container;

                $.each(lang, function (lang, el) {
                    var curLang = lang.replace('_', '-');
                    if (!activeField) {
                        activeField = el;
                    } else {
                        if (curLang === activeLanguage) {
                            $(activeField).closest(containerClass).hide()
                            activeField = el;
                        } else {
                            $(el).closest(containerClass).hide();
                        }
                    }
                });
                
                container = $(activeField).closest(containerClass).find('label');
                if (container.html()) {
                    container.html(container.html().replace(/ \[.+\]/, ''));
                }
            });
        }

        function getActiveLanguage(selector) {
            $options = selector.find('option');
            language = 'undefined';
            $.each($options, function(idx, opt) {
                if ($(opt).prop('selected')) {
                    language = $(opt).attr('value').split('/')[1];
                }
            });
            return language;
        }

        if ($('body').hasClass('change-form')) {
            // Get active language from language selector
            var activeLanguage = getActiveLanguage($('#id_language'));

            // Group normal fields and fields in (existing) stacked inlines
            var grouper = new TranslationFieldGrouper({
                $fields: $('.mt').filter('input:visible, textarea:visible, select:visible, iframe').filter(':parents(.inline-tabular)')
            });
            activateFields(grouper.groupedTranslations, activeLanguage, '.form-row');

            // Group fields in (existing) tabular inlines
            $('div.inline-group.inline-tabular').each(function () {
                var tabularInlineGroup = new TabularInlineGroup({
                    'el': $(this).parent()
                });
                activateFields(tabularInlineGroup.getAllGroupedTranslations(), activeLanguage, '.form-cell');
            });
        }
    });
}());
