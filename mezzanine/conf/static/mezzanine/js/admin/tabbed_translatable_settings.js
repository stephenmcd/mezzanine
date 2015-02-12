/*jslint white: true, onevar: true, undef: true, nomen: true, eqeqeq: true,
  plusplus: true, bitwise: true, regexp: true, newcap: true, immed: true */
var django;

(function () {
    var jQuery = window.jQuery || $ || django.jQuery;

    jQuery(function ($) {
        var TranslationFieldMezzanine = function (options) {
            this.el = options.el;
            this.id = '';
            this.lang = '';
            this.groupId = '';

            this.init = function () {
                this.id = $(this.el).attr('id');
                var bits = this.id.split('_modeltranslation_');
                this.groupId = bits[0];
                this.lang = bits[1];
            };

            this.init();
        };

        var TranslationFieldGrouperMezzanine = function (options) {
            this.$fields = options.$fields;
            this.groupedTranslations = {};

            this.init = function () {
                this.groupedTranslations = this.getGroupedTranslations();
            };

            this.getGroupedTranslations = function () {
                /**
                 * Returns a grouped set of all translatable settings fields.
                 * The returned datastructure will look something like this:
                 *
                 * {
                 *     'id_SETTING_NAME': {
                 *         'en': HTMLInputElement,
                 *         'de': HTMLInputElement,
                 *         'zh_tw': HTMLInputElement
                 *     },
                 *     'id_OTHER_SETTING_NAME': {
                 *         'en': HTMLInputElement,
                 *         'de': HTMLInputElement,
                 *         'zh_tw': HTMLInputElement
                 *     },
                 * }
                 */
                var self = this;
                this.$fields.each(function (idx, el) {
                      var tfield = new TranslationFieldMezzanine({el: el});
                      if (!self.groupedTranslations[tfield.groupId]) {
                          self.groupedTranslations[tfield.groupId] = {};
                      }
                      self.groupedTranslations[tfield.groupId][tfield.lang] = el;
                });
                return this.groupedTranslations;
            };

            this.init();
        };

        function activateFields(groupedTranslations) {
            var options = $('#id_language').find('option'),
                language;
            $.each(options, function(idx, opt) {
                if ($(opt).prop('selected')) {
                    language = $(opt).attr('value').split('/')[1];
                }
            });

            $.each(groupedTranslations, function (groupId, lang) {
                var activeField = null;

                $.each(lang, function (lang, el) {
                    if (!activeField) {
                        activeField = el;
                    } else {
                        if (language === lang.replace('_', '-')) {
                            $(activeField).parent().hide();
                            activeField = el;
                        } else {
                            $(el).parent().hide();
                        }
                    }
                });
            });
        }

        if ($('body').hasClass('change-list')) {
            // Group normal fields and fields in (existing) stacked inlines
            var grouper = new TranslationFieldGrouperMezzanine({
                $fields: $('.modeltranslation').filter('input:visible, textarea:visible, select:visible, iframe')
            });
            activateFields(grouper.groupedTranslations);
        }
    });
}());
