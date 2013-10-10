/*! Magnific Popup - v0.9.6 - 2013-09-29
* http://dimsemenov.com/plugins/magnific-popup/
* Copyright (c) 2013 Dmitry Semenov; */
(function ($) {
  var CLOSE_EVENT = "Close",
    BEFORE_CLOSE_EVENT = "BeforeClose",
    AFTER_CLOSE_EVENT = "AfterClose",
    BEFORE_APPEND_EVENT = "BeforeAppend",
    MARKUP_PARSE_EVENT = "MarkupParse",
    OPEN_EVENT = "Open",
    CHANGE_EVENT = "Change",
    NS = "mfp",
    EVENT_NS = "." + NS,
    READY_CLASS = "mfp-ready",
    REMOVING_CLASS = "mfp-removing",
    PREVENT_CLOSE_CLASS = "mfp-prevent-close";
  var mfp, MagnificPopup = function () {},
    _isJQ = !! window.jQuery,
    _prevStatus, _window = $(window),
    _body, _document, _prevContentType, _wrapClasses, _currPopupType;
  var _mfpOn = function (name, f) {
      mfp.ev.on(NS + name + EVENT_NS, f)
    },
    _getEl = function (className, appendTo, html, raw) {
      var el = document.createElement("div");
      el.className = "mfp-" + className;
      if (html) el.innerHTML = html;
      if (!raw) {
        el = $(el);
        if (appendTo) el.appendTo(appendTo)
      } else if (appendTo) appendTo.appendChild(el);
      return el
    },
    _mfpTrigger = function (e, data) {
      mfp.ev.triggerHandler(NS + e, data);
      if (mfp.st.callbacks) {
        e = e.charAt(0).toLowerCase() + e.slice(1);
        if (mfp.st.callbacks[e]) mfp.st.callbacks[e].apply(mfp, $.isArray(data) ? data : [data])
      }
    },
    _setFocus = function () {
      (mfp.st.focus ? mfp.content.find(mfp.st.focus).eq(0) : mfp.wrap).focus()
    },
    _getCloseBtn = function (type) {
      if (type !== _currPopupType || !mfp.currTemplate.closeBtn) {
        mfp.currTemplate.closeBtn = $(mfp.st.closeMarkup.replace("%title%", mfp.st.tClose));
        _currPopupType = type
      }
      return mfp.currTemplate.closeBtn
    },
    _checkInstance = function () {
      if (!$.magnificPopup.instance) {
        mfp = new MagnificPopup;
        mfp.init();
        $.magnificPopup.instance = mfp
      }
    },
    _checkIfClose = function (target) {
      if ($(target).hasClass(PREVENT_CLOSE_CLASS)) return;
      var closeOnContent = mfp.st.closeOnContentClick;
      var closeOnBg = mfp.st.closeOnBgClick;
      if (closeOnContent && closeOnBg) return true;
      else {
        if (!mfp.content || ($(target).hasClass("mfp-close") || mfp.preloader && target === mfp.preloader[0])) return true;
        if (target !== mfp.content[0] && !$.contains(mfp.content[0], target)) {
          if (closeOnBg) if ($.contains(document, target)) return true
        } else if (closeOnContent) return true
      }
      return false
    },
    supportsTransitions = function () {
      var s = document.createElement("p").style,
        v = ["ms", "O", "Moz", "Webkit"];
      if (s["transition"] !== undefined) return true;
      while (v.length) if (v.pop() + "Transition" in s) return true;
      return false
    };
  MagnificPopup.prototype = {
    constructor: MagnificPopup,
    init: function () {
      var appVersion = navigator.appVersion;
      mfp.isIE7 = appVersion.indexOf("MSIE 7.") !== -1;
      mfp.isIE8 = appVersion.indexOf("MSIE 8.") !== -1;
      mfp.isLowIE = mfp.isIE7 || mfp.isIE8;
      mfp.isAndroid = /android/gi.test(appVersion);
      mfp.isIOS = /iphone|ipad|ipod/gi.test(appVersion);
      mfp.supportsTransition = supportsTransitions();
      mfp.probablyMobile = mfp.isAndroid || (mfp.isIOS || /(Opera Mini)|Kindle|webOS|BlackBerry|(Opera Mobi)|(Windows Phone)|IEMobile/i.test(navigator.userAgent));
      _body = $(document.body);
      _document = $(document);
      mfp.popupsCache = {}
    },
    open: function (data) {
      var i;
      if (data.isObj === false) {
        mfp.items = data.items.toArray();
        mfp.index = 0;
        var items = data.items,
          item;
        for (i = 0; i < items.length; i++) {
          item = items[i];
          if (item.parsed) item = item.el[0];
          if (item === data.el[0]) {
            mfp.index = i;
            break
          }
        }
      } else {
        mfp.items = $.isArray(data.items) ? data.items : [data.items];
        mfp.index = data.index || 0
      }
      if (mfp.isOpen) {
        mfp.updateItemHTML();
        return
      }
      mfp.types = [];
      _wrapClasses = "";
      if (data.mainEl && data.mainEl.length) mfp.ev = data.mainEl.eq(0);
      else mfp.ev = _document;
      if (data.key) {
        if (!mfp.popupsCache[data.key]) mfp.popupsCache[data.key] = {};
        mfp.currTemplate = mfp.popupsCache[data.key]
      } else mfp.currTemplate = {};
      mfp.st = $.extend(true, {}, $.magnificPopup.defaults, data);
      mfp.fixedContentPos = mfp.st.fixedContentPos === "auto" ? !mfp.probablyMobile : mfp.st.fixedContentPos;
      if (mfp.st.modal) {
        mfp.st.closeOnContentClick = false;
        mfp.st.closeOnBgClick = false;
        mfp.st.showCloseBtn = false;
        mfp.st.enableEscapeKey = false
      }
      if (!mfp.bgOverlay) {
        mfp.bgOverlay = _getEl("bg").on("click" + EVENT_NS, function () {
          mfp.close()
        });
        mfp.wrap = _getEl("wrap").attr("tabindex", -1).on("click" + EVENT_NS, function (e) {
          if (_checkIfClose(e.target)) mfp.close()
        });
        mfp.container = _getEl("container", mfp.wrap)
      }
      mfp.contentContainer = _getEl("content");
      if (mfp.st.preloader) mfp.preloader = _getEl("preloader", mfp.container, mfp.st.tLoading);
      var modules = $.magnificPopup.modules;
      for (i = 0; i < modules.length; i++) {
        var n = modules[i];
        n = n.charAt(0).toUpperCase() + n.slice(1);
        mfp["init" + n].call(mfp)
      }
      _mfpTrigger("BeforeOpen");
      if (mfp.st.showCloseBtn) if (!mfp.st.closeBtnInside) mfp.wrap.append(_getCloseBtn());
      else {
        _mfpOn(MARKUP_PARSE_EVENT, function (e, template, values, item) {
          values.close_replaceWith = _getCloseBtn(item.type)
        });
        _wrapClasses += " mfp-close-btn-in"
      }
      if (mfp.st.alignTop) _wrapClasses += " mfp-align-top";
      if (mfp.fixedContentPos) mfp.wrap.css({
        overflow: mfp.st.overflowY,
        overflowX: "hidden",
        overflowY: mfp.st.overflowY
      });
      else mfp.wrap.css({
        top: _window.scrollTop(),
        position: "absolute"
      });
      if (mfp.st.fixedBgPos === false || mfp.st.fixedBgPos === "auto" && !mfp.fixedContentPos) mfp.bgOverlay.css({
        height: _document.height(),
        position: "absolute"
      });
      if (mfp.st.enableEscapeKey) _document.on("keyup" + EVENT_NS, function (e) {
        if (e.keyCode === 27) mfp.close()
      });
      _window.on("resize" + EVENT_NS, function () {
        mfp.updateSize()
      });
      if (!mfp.st.closeOnContentClick) _wrapClasses += " mfp-auto-cursor";
      if (_wrapClasses) mfp.wrap.addClass(_wrapClasses);
      var windowHeight = mfp.wH = _window.height();
      var windowStyles = {};
      if (mfp.fixedContentPos) if (mfp._hasScrollBar(windowHeight)) {
        var s = mfp._getScrollbarSize();
        if (s) windowStyles.paddingRight = s
      }
      if (mfp.fixedContentPos) if (!mfp.isIE7) windowStyles.overflow = "hidden";
      else $("body, html").css("overflow", "hidden");
      var classesToadd = mfp.st.mainClass;
      if (mfp.isIE7) classesToadd += " mfp-ie7";
      if (classesToadd) mfp._addClassToMFP(classesToadd);
      mfp.updateItemHTML();
      _mfpTrigger("BuildControls");
      $("html").css(windowStyles);
      mfp.bgOverlay.add(mfp.wrap).prependTo(document.body);
      mfp._lastFocusedEl = document.activeElement;
      setTimeout(function () {
        if (mfp.content) {
          mfp._addClassToMFP(READY_CLASS);
          _setFocus()
        } else mfp.bgOverlay.addClass(READY_CLASS);
        _document.on("focusin" + EVENT_NS, function (e) {
          if (e.target !== mfp.wrap[0] && !$.contains(mfp.wrap[0], e.target)) {
            _setFocus();
            return false
          }
        })
      }, 16);
      mfp.isOpen = true;
      mfp.updateSize(windowHeight);
      _mfpTrigger(OPEN_EVENT);
      return data
    },
    close: function () {
      if (!mfp.isOpen) return;
      _mfpTrigger(BEFORE_CLOSE_EVENT);
      mfp.isOpen = false;
      if (mfp.st.removalDelay && (!mfp.isLowIE && mfp.supportsTransition)) {
        mfp._addClassToMFP(REMOVING_CLASS);
        setTimeout(function () {
          mfp._close()
        }, mfp.st.removalDelay)
      } else mfp._close()
    },
    _close: function () {
      _mfpTrigger(CLOSE_EVENT);
      var classesToRemove = REMOVING_CLASS + " " + READY_CLASS + " ";
      mfp.bgOverlay.detach();
      mfp.wrap.detach();
      mfp.container.empty();
      if (mfp.st.mainClass) classesToRemove += mfp.st.mainClass + " ";
      mfp._removeClassFromMFP(classesToRemove);
      if (mfp.fixedContentPos) {
        var windowStyles = {
          paddingRight: ""
        };
        if (mfp.isIE7) $("body, html").css("overflow", "");
        else windowStyles.overflow = "";
        $("html").css(windowStyles)
      }
      _document.off("keyup" + EVENT_NS + " focusin" + EVENT_NS);
      mfp.ev.off(EVENT_NS);
      mfp.wrap.attr("class", "mfp-wrap").removeAttr("style");
      mfp.bgOverlay.attr("class", "mfp-bg");
      mfp.container.attr("class", "mfp-container");
      if (mfp.st.showCloseBtn && (!mfp.st.closeBtnInside || mfp.currTemplate[mfp.currItem.type] === true)) if (mfp.currTemplate.closeBtn) mfp.currTemplate.closeBtn.detach();
      if (mfp._lastFocusedEl) $(mfp._lastFocusedEl).focus();
      mfp.currItem = null;
      mfp.content = null;
      mfp.currTemplate = null;
      mfp.prevHeight = 0;
      _mfpTrigger(AFTER_CLOSE_EVENT)
    },
    updateSize: function (winHeight) {
      if (mfp.isIOS) {
        var zoomLevel = document.documentElement.clientWidth / window.innerWidth;
        var height = window.innerHeight * zoomLevel;
        mfp.wrap.css("height", height);
        mfp.wH = height
      } else mfp.wH = winHeight || _window.height();
      if (!mfp.fixedContentPos) mfp.wrap.css("height", mfp.wH);
      _mfpTrigger("Resize")
    },
    updateItemHTML: function () {
      var item = mfp.items[mfp.index];
      mfp.contentContainer.detach();
      if (mfp.content) mfp.content.detach();
      if (!item.parsed) item = mfp.parseEl(mfp.index);
      var type = item.type;
      _mfpTrigger("BeforeChange", [mfp.currItem ? mfp.currItem.type : "", type]);
      mfp.currItem = item;
      if (!mfp.currTemplate[type]) {
        var markup = mfp.st[type] ? mfp.st[type].markup : false;
        _mfpTrigger("FirstMarkupParse", markup);
        if (markup) mfp.currTemplate[type] = $(markup);
        else mfp.currTemplate[type] = true
      }
      if (_prevContentType && _prevContentType !== item.type) mfp.container.removeClass("mfp-" + _prevContentType + "-holder");
      var newContent = mfp["get" + type.charAt(0).toUpperCase() + type.slice(1)](item, mfp.currTemplate[type]);
      mfp.appendContent(newContent, type);
      item.preloaded = true;
      _mfpTrigger(CHANGE_EVENT, item);
      _prevContentType = item.type;
      mfp.container.prepend(mfp.contentContainer);
      _mfpTrigger("AfterChange")
    },
    appendContent: function (newContent, type) {
      mfp.content = newContent;
      if (newContent) if (mfp.st.showCloseBtn && (mfp.st.closeBtnInside && mfp.currTemplate[type] === true)) {
        if (!mfp.content.find(".mfp-close").length) mfp.content.append(_getCloseBtn())
      } else mfp.content = newContent;
      else mfp.content = "";
      _mfpTrigger(BEFORE_APPEND_EVENT);
      mfp.container.addClass("mfp-" + type + "-holder");
      mfp.contentContainer.append(mfp.content)
    },
    parseEl: function (index) {
      var item = mfp.items[index],
        type = item.type;
      if (item.tagName) item = {
        el: $(item)
      };
      else item = {
        data: item,
        src: item.src
      };
      if (item.el) {
        var types = mfp.types;
        for (var i = 0; i < types.length; i++) if (item.el.hasClass("mfp-" + types[i])) {
          type = types[i];
          break
        }
        item.src = item.el.attr("data-mfp-src");
        if (!item.src) item.src = item.el.attr("href")
      }
      item.type = type || (mfp.st.type || "inline");
      item.index = index;
      item.parsed = true;
      mfp.items[index] = item;
      _mfpTrigger("ElementParse", item);
      return mfp.items[index]
    },
    addGroup: function (el, options) {
      var eHandler = function (e) {
          e.mfpEl = this;
          mfp._openClick(e, el, options)
        };
      if (!options) options = {};
      var eName = "click.magnificPopup";
      options.mainEl = el;
      if (options.items) {
        options.isObj = true;
        el.off(eName).on(eName, eHandler)
      } else {
        options.isObj = false;
        if (options.delegate) el.off(eName).on(eName, options.delegate, eHandler);
        else {
          options.items = el;
          el.off(eName).on(eName, eHandler)
        }
      }
    },
    _openClick: function (e, el, options) {
      var midClick = options.midClick !== undefined ? options.midClick : $.magnificPopup.defaults.midClick;
      if (!midClick && (e.which === 2 || (e.ctrlKey || e.metaKey))) return;
      var disableOn = options.disableOn !== undefined ? options.disableOn : $.magnificPopup.defaults.disableOn;
      if (disableOn) if ($.isFunction(disableOn)) {
        if (!disableOn.call(mfp)) return true
      } else if (_window.width() < disableOn) return true;
      if (e.type) {
        e.preventDefault();
        if (mfp.isOpen) e.stopPropagation()
      }
      options.el = $(e.mfpEl);
      if (options.delegate) options.items = el.find(options.delegate);
      mfp.open(options)
    },
    updateStatus: function (status, text) {
      if (mfp.preloader) {
        if (_prevStatus !== status) mfp.container.removeClass("mfp-s-" + _prevStatus);
        if (!text && status === "loading") text = mfp.st.tLoading;
        var data = {
          status: status,
          text: text
        };
        _mfpTrigger("UpdateStatus", data);
        status = data.status;
        text = data.text;
        mfp.preloader.html(text);
        mfp.preloader.find("a").on("click", function (e) {
          e.stopImmediatePropagation()
        });
        mfp.container.addClass("mfp-s-" + status);
        _prevStatus = status
      }
    },
    _addClassToMFP: function (cName) {
      mfp.bgOverlay.addClass(cName);
      mfp.wrap.addClass(cName)
    },
    _removeClassFromMFP: function (cName) {
      this.bgOverlay.removeClass(cName);
      mfp.wrap.removeClass(cName)
    },
    _hasScrollBar: function (winHeight) {
      return (mfp.isIE7 ? _document.height() : document.body.scrollHeight) > (winHeight || _window.height())
    },
    _parseMarkup: function (template, values, item) {
      var arr;
      if (item.data) values = $.extend(item.data, values);
      _mfpTrigger(MARKUP_PARSE_EVENT, [template, values, item]);
      $.each(values, function (key, value) {
        if (value === undefined || value === false) return true;
        arr = key.split("_");
        if (arr.length > 1) {
          var el = template.find(EVENT_NS + "-" + arr[0]);
          if (el.length > 0) {
            var attr = arr[1];
            if (attr === "replaceWith") {
              if (el[0] !== value[0]) el.replaceWith(value)
            } else if (attr === "img") if (el.is("img")) el.attr("src", value);
            else el.replaceWith('<img src="' + value + '" class="' + el.attr("class") + '" />');
            else el.attr(arr[1], value)
          }
        } else template.find(EVENT_NS + "-" + key).html(value)
      })
    },
    _getScrollbarSize: function () {
      if (mfp.scrollbarSize === undefined) {
        var scrollDiv = document.createElement("div");
        scrollDiv.id = "mfp-sbm";
        scrollDiv.style.cssText = "width: 99px; height: 99px; overflow: scroll; position: absolute; top: -9999px;";
        document.body.appendChild(scrollDiv);
        mfp.scrollbarSize = scrollDiv.offsetWidth - scrollDiv.clientWidth;
        document.body.removeChild(scrollDiv)
      }
      return mfp.scrollbarSize
    }
  };
  $.magnificPopup = {
    instance: null,
    proto: MagnificPopup.prototype,
    modules: [],
    open: function (options, index) {
      _checkInstance();
      if (!options) options = {};
      else options = $.extend(true, {}, options);
      options.isObj = true;
      options.index = index || 0;
      return this.instance.open(options)
    },
    close: function () {
      return $.magnificPopup.instance && $.magnificPopup.instance.close()
    },
    registerModule: function (name, module) {
      if (module.options) $.magnificPopup.defaults[name] = module.options;
      $.extend(this.proto, module.proto);
      this.modules.push(name)
    },
    defaults: {
      disableOn: 0,
      key: null,
      midClick: false,
      mainClass: "",
      preloader: true,
      focus: "",
      closeOnContentClick: false,
      closeOnBgClick: true,
      closeBtnInside: true,
      showCloseBtn: true,
      enableEscapeKey: true,
      modal: false,
      alignTop: false,
      removalDelay: 0,
      fixedContentPos: "auto",
      fixedBgPos: "auto",
      overflowY: "auto",
      closeMarkup: '<button title="%title%" type="button" class="mfp-close">&times;</button>',
      tClose: "Close (Esc)",
      tLoading: "Loading..."
    }
  };
  $.fn.magnificPopup = function (options) {
    _checkInstance();
    var jqEl = $(this);
    if (typeof options === "string") if (options === "open") {
      var items, itemOpts = _isJQ ? jqEl.data("magnificPopup") : jqEl[0].magnificPopup,
        index = parseInt(arguments[1], 10) || 0;
      if (itemOpts.items) items = itemOpts.items[index];
      else {
        items = jqEl;
        if (itemOpts.delegate) items = items.find(itemOpts.delegate);
        items = items.eq(index)
      }
      mfp._openClick({
        mfpEl: items
      }, jqEl, itemOpts)
    } else {
      if (mfp.isOpen) mfp[options].apply(mfp, Array.prototype.slice.call(arguments, 1))
    } else {
      options = $.extend(true, {}, options);
      if (_isJQ) jqEl.data("magnificPopup", options);
      else jqEl[0].magnificPopup = options;
      mfp.addGroup(jqEl, options)
    }
    return jqEl
  };
  var _imgInterval, _getTitle = function (item) {
      if (item.data && item.data.title !== undefined) return item.data.title;
      var src = mfp.st.image.titleSrc;
      if (src) if ($.isFunction(src)) return src.call(mfp, item);
      else if (item.el) return item.el.attr(src) || "";
      return ""
    };
  $.magnificPopup.registerModule("image", {
    options: {
      markup: '<div class="mfp-figure">' + '<div class="mfp-close"></div>' + '<div class="mfp-img"></div>' + '<div class="mfp-bottom-bar">' + '<div class="mfp-title"></div>' + '<div class="mfp-counter"></div>' + "</div>" + "</div>",
      cursor: "mfp-zoom-out-cur",
      titleSrc: "title",
      verticalFit: true,
      tError: '<a href="%url%">The image</a> could not be loaded.'
    },
    proto: {
      initImage: function () {
        var imgSt = mfp.st.image,
          ns = ".image";
        mfp.types.push("image");
        _mfpOn(OPEN_EVENT + ns, function () {
          if (mfp.currItem.type === "image" && imgSt.cursor) _body.addClass(imgSt.cursor)
        });
        _mfpOn(CLOSE_EVENT + ns, function () {
          if (imgSt.cursor) _body.removeClass(imgSt.cursor);
          _window.off("resize" + EVENT_NS)
        });
        _mfpOn("Resize" + ns, mfp.resizeImage);
        if (mfp.isLowIE) _mfpOn("AfterChange", mfp.resizeImage)
      },
      resizeImage: function () {
        var item = mfp.currItem;
        if (!item || !item.img) return;
        if (mfp.st.image.verticalFit) {
          var decr = 0;
          if (mfp.isLowIE) decr = parseInt(item.img.css("padding-top"), 10) + parseInt(item.img.css("padding-bottom"), 10);
          item.img.css("max-height", mfp.wH - decr)
        }
      },
      _onImageHasSize: function (item) {
        if (item.img) {
          item.hasSize = true;
          if (_imgInterval) clearInterval(_imgInterval);
          item.isCheckingImgSize = false;
          _mfpTrigger("ImageHasSize", item);
          if (item.imgHidden) {
            if (mfp.content) mfp.content.removeClass("mfp-loading");
            item.imgHidden = false
          }
        }
      },
      findImageSize: function (item) {
        var counter = 0,
          img = item.img[0],
          mfpSetInterval = function (delay) {
            if (_imgInterval) clearInterval(_imgInterval);
            _imgInterval = setInterval(function () {
              if (img.naturalWidth > 0) {
                mfp._onImageHasSize(item);
                return
              }
              if (counter > 200) clearInterval(_imgInterval);
              counter++;
              if (counter === 3) mfpSetInterval(10);
              else if (counter === 40) mfpSetInterval(50);
              else if (counter === 100) mfpSetInterval(500)
            }, delay)
          };
        mfpSetInterval(1)
      },
      getImage: function (item, template) {
        var guard = 0,
          onLoadComplete = function () {
            if (item) if (item.img[0].complete) {
              item.img.off(".mfploader");
              if (item === mfp.currItem) {
                mfp._onImageHasSize(item);
                mfp.updateStatus("ready")
              }
              item.hasSize = true;
              item.loaded = true;
              _mfpTrigger("ImageLoadComplete")
            } else {
              guard++;
              if (guard < 200) setTimeout(onLoadComplete, 100);
              else onLoadError()
            }
          },
          onLoadError = function () {
            if (item) {
              item.img.off(".mfploader");
              if (item === mfp.currItem) {
                mfp._onImageHasSize(item);
                mfp.updateStatus("error", imgSt.tError.replace("%url%", item.src))
              }
              item.hasSize = true;
              item.loaded = true;
              item.loadError = true
            }
          },
          imgSt = mfp.st.image;
        var el = template.find(".mfp-img");
        if (el.length) {
          var img = document.createElement("img");
          img.className = "mfp-img";
          item.img = $(img).on("load.mfploader", onLoadComplete).on("error.mfploader", onLoadError);
          img.src = item.src;
          if (el.is("img")) item.img = item.img.clone();
          if (item.img[0].naturalWidth > 0) item.hasSize = true
        }
        mfp._parseMarkup(template, {
          title: _getTitle(item),
          img_replaceWith: item.img
        }, item);
        mfp.resizeImage();
        if (item.hasSize) {
          if (_imgInterval) clearInterval(_imgInterval);
          if (item.loadError) {
            template.addClass("mfp-loading");
            mfp.updateStatus("error", imgSt.tError.replace("%url%", item.src))
          } else {
            template.removeClass("mfp-loading");
            mfp.updateStatus("ready")
          }
          return template
        }
        mfp.updateStatus("loading");
        item.loading = true;
        if (!item.hasSize) {
          item.imgHidden = true;
          template.addClass("mfp-loading");
          mfp.findImageSize(item)
        }
        return template
      }
    }
  });
  var hasMozTransform, getHasMozTransform = function () {
      if (hasMozTransform === undefined) hasMozTransform = document.createElement("p").style.MozTransform !== undefined;
      return hasMozTransform
    };
  $.magnificPopup.registerModule("zoom", {
    options: {
      enabled: false,
      easing: "ease-in-out",
      duration: 300,
      opener: function (element) {
        return element.is("img") ? element : element.find("img")
      }
    },
    proto: {
      initZoom: function () {
        var zoomSt = mfp.st.zoom,
          ns = ".zoom",
          image;
        if (!zoomSt.enabled || !mfp.supportsTransition) return;
        var duration = zoomSt.duration,
          getElToAnimate = function (image) {
            var newImg = image.clone().removeAttr("style").removeAttr("class").addClass("mfp-animated-image"),
              transition = "all " + zoomSt.duration / 1E3 + "s " + zoomSt.easing,
              cssObj = {
                position: "fixed",
                zIndex: 9999,
                left: 0,
                top: 0,
                "-webkit-backface-visibility": "hidden"
              },
              t = "transition";
            cssObj["-webkit-" + t] = cssObj["-moz-" + t] = cssObj["-o-" + t] = cssObj[t] = transition;
            newImg.css(cssObj);
            return newImg
          },
          showMainContent = function () {
            mfp.content.css("visibility", "visible")
          },
          openTimeout, animatedImg;
        _mfpOn("BuildControls" + ns, function () {
          if (mfp._allowZoom()) {
            clearTimeout(openTimeout);
            mfp.content.css("visibility", "hidden");
            image = mfp._getItemToZoom();
            if (!image) {
              showMainContent();
              return
            }
            animatedImg = getElToAnimate(image);
            animatedImg.css(mfp._getOffset());
            mfp.wrap.append(animatedImg);
            openTimeout = setTimeout(function () {
              animatedImg.css(mfp._getOffset(true));
              openTimeout = setTimeout(function () {
                showMainContent();
                setTimeout(function () {
                  animatedImg.remove();
                  image = animatedImg = null;
                  _mfpTrigger("ZoomAnimationEnded")
                }, 16)
              }, duration)
            }, 16)
          }
        });
        _mfpOn(BEFORE_CLOSE_EVENT + ns, function () {
          if (mfp._allowZoom()) {
            clearTimeout(openTimeout);
            mfp.st.removalDelay = duration;
            if (!image) {
              image = mfp._getItemToZoom();
              if (!image) return;
              animatedImg = getElToAnimate(image)
            }
            animatedImg.css(mfp._getOffset(true));
            mfp.wrap.append(animatedImg);
            mfp.content.css("visibility", "hidden");
            setTimeout(function () {
              animatedImg.css(mfp._getOffset())
            }, 16)
          }
        });
        _mfpOn(CLOSE_EVENT + ns, function () {
          if (mfp._allowZoom()) {
            showMainContent();
            if (animatedImg) animatedImg.remove();
            image = null
          }
        })
      },
      _allowZoom: function () {
        return mfp.currItem.type === "image"
      },
      _getItemToZoom: function () {
        if (mfp.currItem.hasSize) return mfp.currItem.img;
        else return false
      },
      _getOffset: function (isLarge) {
        var el;
        if (isLarge) el = mfp.currItem.img;
        else el = mfp.st.zoom.opener(mfp.currItem.el || mfp.currItem);
        var offset = el.offset();
        var paddingTop = parseInt(el.css("padding-top"), 10);
        var paddingBottom = parseInt(el.css("padding-bottom"), 10);
        offset.top -= $(window).scrollTop() - paddingTop;
        var obj = {
          width: el.width(),
          height: (_isJQ ? el.innerHeight() : el[0].offsetHeight) - paddingBottom - paddingTop
        };
        if (getHasMozTransform()) obj["-moz-transform"] = obj["transform"] = "translate(" + offset.left + "px," + offset.top + "px)";
        else {
          obj.left = offset.left;
          obj.top = offset.top
        }
        return obj
      }
    }
  });
  var _getLoopedId = function (index) {
      var numSlides = mfp.items.length;
      if (index > numSlides - 1) return index - numSlides;
      else if (index < 0) return numSlides + index;
      return index
    },
    _replaceCurrTotal = function (text, curr, total) {
      return text.replace("%curr%", curr + 1).replace("%total%", total)
    };
  $.magnificPopup.registerModule("gallery", {
    options: {
      enabled: false,
      arrowMarkup: '<button title="%title%" type="button" class="mfp-arrow mfp-arrow-%dir%"></button>',
      preload: [0, 2],
      navigateByImgClick: true,
      arrows: true,
      tPrev: "Previous (Left arrow key)",
      tNext: "Next (Right arrow key)",
      tCounter: "%curr% of %total%"
    },
    proto: {
      initGallery: function () {
        var gSt = mfp.st.gallery,
          ns = ".mfp-gallery",
          supportsFastClick = Boolean($.fn.mfpFastClick);
        mfp.direction = true;
        if (!gSt || !gSt.enabled) return false;
        _wrapClasses += " mfp-gallery";
        _mfpOn(OPEN_EVENT + ns, function () {
          if (gSt.navigateByImgClick) mfp.wrap.on("click" + ns, ".mfp-img", function () {
            if (mfp.items.length > 1) {
              mfp.next();
              return false
            }
          });
          _document.on("keydown" + ns, function (e) {
            if (e.keyCode === 37) mfp.prev();
            else if (e.keyCode === 39) mfp.next()
          })
        });
        _mfpOn("UpdateStatus" + ns, function (e, data) {
          if (data.text) data.text = _replaceCurrTotal(data.text, mfp.currItem.index, mfp.items.length)
        });
        _mfpOn(MARKUP_PARSE_EVENT + ns, function (e, element, values, item) {
          var l = mfp.items.length;
          values.counter = l > 1 ? _replaceCurrTotal(gSt.tCounter, item.index, l) : ""
        });
        _mfpOn("BuildControls" + ns, function () {
          if (mfp.items.length > 1 && (gSt.arrows && !mfp.arrowLeft)) {
            var markup = gSt.arrowMarkup,
              arrowLeft = mfp.arrowLeft = $(markup.replace("%title%", gSt.tPrev).replace("%dir%", "left")).addClass(PREVENT_CLOSE_CLASS),
              arrowRight = mfp.arrowRight = $(markup.replace("%title%", gSt.tNext).replace("%dir%", "right")).addClass(PREVENT_CLOSE_CLASS);
            var eName = supportsFastClick ? "mfpFastClick" : "click";
            arrowLeft[eName](function () {
              mfp.prev()
            });
            arrowRight[eName](function () {
              mfp.next()
            });
            if (mfp.isIE7) {
              _getEl("b", arrowLeft[0], false, true);
              _getEl("a", arrowLeft[0], false, true);
              _getEl("b", arrowRight[0], false, true);
              _getEl("a", arrowRight[0], false, true)
            }
            mfp.container.append(arrowLeft.add(arrowRight))
          }
        });
        _mfpOn(CHANGE_EVENT + ns, function () {
          if (mfp._preloadTimeout) clearTimeout(mfp._preloadTimeout);
          mfp._preloadTimeout = setTimeout(function () {
            mfp.preloadNearbyImages();
            mfp._preloadTimeout = null
          }, 16)
        });
        _mfpOn(CLOSE_EVENT + ns, function () {
          _document.off(ns);
          mfp.wrap.off("click" + ns);
          if (mfp.arrowLeft && supportsFastClick) mfp.arrowLeft.add(mfp.arrowRight).destroyMfpFastClick();
          mfp.arrowRight = mfp.arrowLeft = null
        })
      },
      next: function () {
        mfp.direction = true;
        mfp.index = _getLoopedId(mfp.index + 1);
        mfp.updateItemHTML()
      },
      prev: function () {
        mfp.direction = false;
        mfp.index = _getLoopedId(mfp.index - 1);
        mfp.updateItemHTML()
      },
      goTo: function (newIndex) {
        mfp.direction = newIndex >= mfp.index;
        mfp.index = newIndex;
        mfp.updateItemHTML()
      },
      preloadNearbyImages: function () {
        var p = mfp.st.gallery.preload,
          preloadBefore = Math.min(p[0], mfp.items.length),
          preloadAfter = Math.min(p[1], mfp.items.length),
          i;
        for (i = 1; i <= (mfp.direction ? preloadAfter : preloadBefore); i++) mfp._preloadItem(mfp.index + i);
        for (i = 1; i <= (mfp.direction ? preloadBefore : preloadAfter); i++) mfp._preloadItem(mfp.index - i)
      },
      _preloadItem: function (index) {
        index = _getLoopedId(index);
        if (mfp.items[index].preloaded) return;
        var item = mfp.items[index];
        if (!item.parsed) item = mfp.parseEl(index);
        _mfpTrigger("LazyLoad", item);
        if (item.type === "image") item.img = $('<img class="mfp-img" />').on("load.mfploader", function () {
          item.hasSize = true
        }).on("error.mfploader", function () {
          item.hasSize = true;
          item.loadError = true;
          _mfpTrigger("LazyLoadError", item)
        }).attr("src", item.src);
        item.preloaded = true
      }
    }
  })
})(window.jQuery || window.Zepto);
