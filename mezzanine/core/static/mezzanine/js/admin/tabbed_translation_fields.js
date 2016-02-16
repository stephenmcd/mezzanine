/*jslint white: true, onevar: true, undef: true, nomen: true, eqeqeq: true,
  plusplus: true, bitwise: true, regexp: true, newcap: true, immed: true */
var django;

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
                var clsBits = this.cls.substring(TranslationField.cssPrefix.length, this.cls.length).split('-');
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
            };

            this.init();
        };

        function createTabs(groupedTranslations) {
            var tabs = [];
            $.each(groupedTranslations, function (groupId, lang) {
                var tabsContainer = $('<div class="form-row"></div>'),
                    tabsList = $('<ul></ul>'),
                    insertionPoint;
                tabsContainer.append(tabsList);
                $.each(lang, function (lang, el) {
                    var container = $(el).closest('.form-row'),
                        label = $('label', container),
                        fieldLabel = container.find('label'),
                        tabId = 'tab_' + $(el).attr('id'),
                        panel,
                        tab;
                    // Remove language and brackets from field label, they are
                    // displayed in the tab already.
                    if (fieldLabel.html()) {
                        fieldLabel.html(fieldLabel.html().replace(/ \[.+\]/, ''));
                    }
                    if (!insertionPoint) {
                        insertionPoint = {
                            'insert': container.prev().length ? 'after' : container.next().length ? 'prepend' : 'append',
                            'el': container.prev().length ? container.prev() : container.parent()
                        };
                    }
                    container.find('script').remove();
                    panel = $('<div id="' + tabId + '"></div>').append(container);
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

        var TabularInlineGroup = function (options) {
            this.$el = options.el;
            this.$table = null;
            this.translationColumns = [];

            this.init = function () {
                this.$table = this.$el.find('.items');
            };

            this.getAllGroupedTranslations = function () {
                var self = this;
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
                return thGrouper.groupedTranslations;
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

        function createTabularTabs(groupedTranslations, parentElement, index) {
            var tabs = [],
                tabsSwitchName = 'tabular-fake-tab-' + index,
                tabsSwitchContainer = $('<div id="' + tabsSwitchName + '"></div>'),
                tabsSwitchList = $('<ul>'),
                tabsSwitchInit = true;
            tabsSwitchContainer.append(tabsSwitchList);

            $.each(groupedTranslations, function (groupId, lang) {
                var tabsContainer = $('<div class="form-cell"></div>'),
                    tabsList = $('<ul></ul>'),
                    insertionPoint;
                tabsContainer.append(tabsList);

              $.each(lang, function (lang, el) {
                  var $container = $(el).closest('.form-cell'),
                      $panel,
                      $tab,
                      tabId = 'tab_' + $(el).attr('id');
                  if (!insertionPoint) {
                      insertionPoint = {
                          'insert': $container.prev().length ? 'after' : $container.next().length ? 'prepend' : 'append',
                          'el': $container.prev().length ? $container.prev() : $container.parent()
                      };
                  }
                  $panel = $('<div id="' + tabId + '"></div>').append($container);
                  $container.removeClass('form-cell');

                  // TODO: Setting the required state based on the default field is naive.
                  // The user might have tweaked his admin. We somehow have to keep track of the
                  // column indexes _before_ the tds have been moved around.
                  $tab = $('<li' + ($(el).hasClass('mt-default') ? ' class="required"' : '') + '><a href="#' + tabId + '">' + lang.replace('_', '-') + '</a></li>');
                  tabsList.append($tab);
                  tabsContainer.append($panel);
                  if (tabsSwitchInit) {
                      var tabName = tabsSwitchName + '-' + lang.replace('_', '-');
                      $panel = $('<div id="' + tabName + '"></div>');
                      $tab = $('<li' + ($(el).hasClass('mt-default') ? ' class="required"' : '') + '><a href="#' + tabName + '">' + lang.replace('_', '-') + '</a></li>');
                      tabsSwitchList.append($tab);
                      tabsSwitchContainer.append($panel);
                  }
              });
              tabsSwitchInit = false;

              insertionPoint.el[insertionPoint.insert](tabsContainer);
              tabsContainer.tabs();
              tabsContainer.find('ul').hide();
              tabs.push(tabsContainer);
            });

            if (tabs.length === 0) { return null; }
            parentElement.parent().prepend(tabsSwitchContainer);
            tabsSwitchContainer.tabs({
                select: function (event, ui) {
                    $.each(tabs, function(idx, tab) {
                        tab.tabs('select', ui.index);
                    });
                },
                activate: function (event, ui) {
                    $.each(tabs, function(idx, tab) {
                        tab.tabs('option', 'active', ui.newTab.index());
                    });
                }
            });

            return tabsSwitchContainer;
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

            this.switchAllTabs = function (event, ui) {
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

        if ($('body').hasClass('change-form')) {
            // Group normal fields and fields in (existing) stacked inlines
            var grouper = new TranslationFieldGrouper({
                $fields: $('.mt').filter('input, textarea, select, iframe').filter(':parents(.inline-tabular)')
            });
            var tabs = createTabs(grouper.groupedTranslations);

            // Group fields in (existing) tabular inlines
            $('div.inline-group.inline-tabular').each(function (index) {
              $(this).wrap('<div>');
              var tabularInlineGroup = new TabularInlineGroup({ 'el': $(this).parent() });
              var tab = createTabularTabs(tabularInlineGroup.getAllGroupedTranslations(), tabularInlineGroup.$table, index);
              if (tab) { tabs.push(tab); }
           });

            TabsSwitcher({ tabs: tabs });
        }
    });
}());
