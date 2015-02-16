/*jslint white: true, onevar: true, undef: true, nomen: true, eqeqeq: true,
  plusplus: true, bitwise: true, regexp: true, newcap: true, immed: true */
var django;

(function () {
    var jQuery = window.jQuery || $ || django.jQuery;

    jQuery(function ($) {
        var TranslationField = function (options) {
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

        var TranslationFieldGrouper = function (options) {
            this.$fields = options.$fields;
            this.groupedTranslations = {};

            this.init = function () {
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
                    var tfield = new TranslationField({el: el});
                    if (!self.groupedTranslations[tfield.groupId]) {
                        self.groupedTranslations[tfield.groupId] = {};
                    }
                    self.groupedTranslations[tfield.groupId][tfield.lang] = el;
                });
            };

            this.init();
        };

        function createTabs(groupedTranslations) {
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
                            'insert': container.prev().length ? 'after' : container.next().length ? 'prepend' : 'append',
                            'el': container.prev().length ? container.prev() : container.parent()
                        };
                    }
                    divContainer.html(container.html());
                    container.remove();
                    panel = $('<div id="' + tabId + '"></div>').append(divContainer);
                    tab = $('<li' + (label.hasClass('required') ? ' class="required"' : '') + '><a href="#' + tabId + '">' + lang.replace('_', '-') + '</a></li>');
                    tabsList.append(tab);
                    tabsContainer.append(panel);
                });
                insertionPoint.el[insertionPoint.insert](tabsContainer);
                tabsContainer.tabs();
                tabs.push(tabsContainer);
            });
            return tabs;
        }

        var TabsSwitcher = function (options) {
            this.tabs = options.tabs;
            this.switching = false;

            this.init = function() {
                var self = this;
                $.each(tabs, function (idx, tab) {
                    tab.on('tabsselect', self.switchAllTabs);
                    tab.on('tabsactivate', self.switchAllTabs);
                });
            };

            this.switchAllTabsSelect = function (event, ui) {
                if (!switching) {
                    switching = true;
                    $.each(tabs, function (idx, tab) {
                        try {
                            tab.tabs('option', 'active', ui.newTab.index());
                        } catch (e) {
                            tab.tabs('select', ui.index);
                        }
                    });
                    switching = false;
                }
            };
            
            this.init();
        };

        if ($('body').hasClass('change-list')) {
            var grouper = new TranslationFieldGrouper({ $fields: $('.modeltranslation').filter('input, textarea, select, iframe') });
            TabsSwitcher({ tabs: createTabs(grouper.groupedTranslations) });
        }
    });
}());
