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

        function createTabsMezzanine(groupedTranslations) {
            var tabs = [];
            $.each(groupedTranslations, function (groupId, lang) {
                var tabsContainer = $('<p></p>'),
                    tabsList = $('<ul></ul>'),
                    insertionPoint;
                tabsContainer.append(tabsList);
                $.each(lang, function (lang, el) {
                    var container = $(el).parent(),
                        divContainer = $('<div>'),
                        label = $('label', container),
                        fieldLabel = container.find('label'),
                        tabId = 'tab_' + $(el).attr('id'),
                        panel,
                        tab;
                    if (!insertionPoint) {
                        insertionPoint = {
                            'insert': container.prev().length ? 'after' :
                                container.next().length ? 'prepend' : 'append',
                            'el': container.prev().length ? container.prev() : container.parent()
                        };
                    }
                    divContainer.html(container.html());
                    container.remove();
                    panel = $('<div id="' + tabId + '"></div>').append(divContainer);
                    tab = $('<li' + (label.hasClass('required') ? ' class="required"' : '') +
                            '><a href="#' + tabId + '">' + lang.replace('_', '-') + '</a></li>');
                    tabsList.append(tab);
                    tabsContainer.append(panel);
                });
                insertionPoint.el[insertionPoint.insert](tabsContainer);
                tabsContainer.tabs();
                tabsContainer.find('ul').hide();
                tabs.push(tabsContainer);
            });
            return tabs;
        }

        var MainSwitchMezzanine = {
            languages: [],
            $select: $('<select>'),

            init: function(groupedTranslations, tabs) {
                var self = this;
                $.each(groupedTranslations, function (id, languages) {
                    $.each(languages, function (lang) {
                        if ($.inArray(lang, self.languages) < 0) {
                            self.languages.push(lang);
                        }
                    });
                });
                $.each(this.languages, function (idx, language) {
                    self.$select.append($('<option value="' + idx + '">' +
                                        language.replace('_', '-') + '</option>'));
                });
                this.update(tabs);
                self.$select.css({'position': 'fixed', 'right': '25px', 'z-index': 10000});
                $('#content').css({'position': 'relative'});
                $('#content').prepend(self.$select);
            },

            update: function(tabs) {
                var self = this;
                this.$select.change(function () {
                    $.each(tabs, function (idx, tab) {
                        try { //jquery ui => 1.10 api changed, we keep backward compatibility
                            tab.tabs('select', parseInt(self.$select.val(), 10));
                        } catch(e) {
                            tab.tabs('option', 'active', parseInt(self.$select.val(), 10));
                        }
                    });
                });
            },

            activateTab: function(tabs) {
                var self = this;
                $.each(tabs, function (idx, tab) {
                    try { //jquery ui => 1.10 api changed, we keep backward compatibility
                        tab.tabs('select', parseInt(self.$select.val(), 10));
                    } catch(e) {
                        tab.tabs('option', 'active', parseInt(self.$select.val(), 10));
                    }
                });
            }
        };

        if ($('body').hasClass('change-list')) {
            // Group normal fields and fields in (existing) stacked inlines
            var grouper = new TranslationFieldGrouperMezzanine({
                $fields: $('.modeltranslation').filter('input:visible, textarea:visible, select:visible, iframe')
            });
            MainSwitchMezzanine.init(grouper.groupedTranslations, createTabsMezzanine(grouper.groupedTranslations));
        }
    });
}());
