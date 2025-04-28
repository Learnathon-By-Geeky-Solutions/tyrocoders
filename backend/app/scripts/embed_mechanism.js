console.log("loaded embed_mechanisms.js");

// Configuration and Constants
const CONFIG = {
  SESSION_KEY: "ebuddy_session",
  WIDGET_SIZES: {
    small: { height: "680px", width: "384px" },
    normal: { height: "800px", width: "440px" },
    large: { height: "820px", width: "572px" }
  },
  Z_INDEX: {
    HIDDEN: -9249299,
    VISIBLE: 9249299
  },
  DEFAULT_SIZES: {
    widgetSize: "normal",
    buttonSizes: {
      extraLarge: { height: "110px", width: "110px" },
      large: { height: "100px", width: "100px" },
      default: { height: "90px", width: "90px" }
    }
  }
};

// Utility Functions
const createLogger = () => ({
  error: (message, ...args) => console.error(message, ...args),
  log: (message, ...args) => console.log(message, ...args)
});

const logger = createLogger();

// Session Management
class SessionManager {
  static getSessionData() {
    try {
      const session = localStorage.getItem(CONFIG.SESSION_KEY);
      return session ? JSON.parse(session) : null;
    } catch (error) {
      logger.error("Error reading session:", error);
      return null;
    }
  }

  static saveSessionData(data) {
    try {
      const existingSession = this.getSessionData() || {};
      const updatedSession = {
        ...existingSession,
        ...data,
        conversations: [
          ...(existingSession.conversations || []),
          {
            conversationId: data.conversationId,
            chatbotId: data.chatbotId,
            startedAt: new Date().toISOString(),
          },
        ],
      };
      localStorage.setItem(CONFIG.SESSION_KEY, JSON.stringify(updatedSession));
    } catch (error) {
      logger.error("Error saving session:", error);
    }
  }

  static clearSessionData() {
    try {
      localStorage.removeItem(CONFIG.SESSION_KEY);
    } catch (error) {
      logger.error("Error clearing session:", error);
    }
  }
}

// URL Utility
class URLHelper {
  static removeProtocol(url) {
    return url ? url.replace(/^https?:\/\//, "") : "";
  }

  static buildIframeURL(chatbotId, widgetConfig) {
    const baseUrl = this.buildBaseURL(chatbotId);
    const urlObj = new URL(baseUrl);
    const params = this.buildURLParams(chatbotId, widgetConfig);
    
    urlObj.search = params.toString();
    return urlObj.toString();
  }

  static buildBaseURL(chatbotId) {
    const protocol = window.location.protocol === "https:" ? "https" : "http";
    return `${protocol}://${URLHelper.removeProtocol(widgetConfig.ebuddyAddress)}/widget/${chatbotId}`;
  }

  static buildURLParams(chatbotId, widgetConfig) {
    const params = new URLSearchParams();
    this.addConversationParam(params, chatbotId);
    this.addWidgetParams(params, widgetConfig);
    return params;
  }

  static addConversationParam(params, chatbotId) {
    const session = SessionManager.getSessionData();
    const conversation = session?.conversations?.find(conv => 
      conv.chatbotId === chatbotId
    );
    if (conversation) {
      params.append("ebuddy_conversation_id", conversation.conversationId);
    }
  }

  static addWidgetParams(params, widgetConfig) {
    Object.entries(widgetConfig)
      .filter(([, value]) => value !== undefined && value !== null && value !== '')
      .forEach(([key, value]) => params.append(key, value));
  }
}

// Widget Configuration Extractor
class WidgetConfigExtractor {
  static extract() {
    const ebuddyScript = document.querySelector("script[data-name='ebuddy']");
    
    return {
      offsetBottom: ebuddyScript?.getAttribute("data-widget-offset-bottom"),
      offsetRight: ebuddyScript?.getAttribute("data-widget-offset-right"),
      offsetBottomMobile: ebuddyScript?.getAttribute("data-widget-offset-bottom-mobile"),
      offsetRightMobile: ebuddyScript?.getAttribute("data-widget-offset-right-mobile"),
      placement: ebuddyScript?.getAttribute("data-placement") || "right",
      chatbotId: ebuddyScript?.getAttribute("data-chatbot-id"),
      dataUserId: ebuddyScript?.getAttribute("data-user-id"),
      ebuddyAddress: ebuddyScript?.getAttribute("data-address"),
      dataIgnorePaths: ebuddyScript?.getAttribute("data-ignore-paths"),
      dataShowPaths: ebuddyScript?.getAttribute("data-show-paths"),
      dataMovable: ebuddyScript?.getAttribute("data-movable"),
      widgetSize: ebuddyScript?.getAttribute("data-widget-size") || CONFIG.DEFAULT_SIZES.widgetSize,
      widgetButtonSize: ebuddyScript?.getAttribute("data-widget-button-size") || "default"
    };
  }
}

// Widget Renderer
class WidgetRenderer {
  constructor(config) {
    this.config = config;
    this.wrapper = this.createWrapper();
    this.iframe = this.createIframe();
  }

  createWrapper() {
    const wrapper = document.createElement("div");
    wrapper.id = "ebuddy-wrapper";
    wrapper.style.zIndex = CONFIG.Z_INDEX.VISIBLE;
    wrapper.style.background = "transparent";
    wrapper.style.overflow = "hidden";
    wrapper.style.position = "fixed";
    wrapper.style.bottom = "0px";
    
    this.setWrapperPosition(wrapper);
    this.setWrapperSize(wrapper);
    
    return wrapper;
  }

  setWrapperPosition(wrapper) {
    wrapper.style[this.config.placement === "right" ? "right" : "left"] = "0px";
  }

  setWrapperSize(wrapper) {
    const buttonSizes = CONFIG.DEFAULT_SIZES.buttonSizes;
    const size = buttonSizes[this.config.widgetButtonSize] || buttonSizes.default;
    
    wrapper.style.height = size.height;
    wrapper.style.width = size.width;
  }

  createIframe() {
    const iframe = document.createElement("iframe");
    iframe.setAttribute("src", URLHelper.buildIframeURL(this.config.chatbotId, this.config));
    iframe.setAttribute("frameborder", "0");
    iframe.setAttribute("scrolling", "no");
    iframe.setAttribute("allow", "fullscreen; clipboard-read; clipboard-write");
    
    iframe.style.width = "100%";
    iframe.style.height = "100%";
    iframe.style.background = "transparent";
    iframe.style.minHeight = "auto";
    iframe.style.colorScheme = "light";
    iframe.style.pointerEvents = "auto";
    
    iframe.id = "ebuddy";
    
    return iframe;
  }

  render() {
    document.body.appendChild(this.wrapper);
    this.adjustSizeBasedOnScreen();
  }

  adjustSizeBasedOnScreen() {
    const isDesktop = window.matchMedia("(min-width: 800px)").matches;
    const config = this.config;
    
    this.wrapper.style.marginBottom = isDesktop 
      ? config.offsetBottom || "0px" 
      : config.offsetBottomMobile || "0px";
    
    this.wrapper.style.marginRight = isDesktop 
      ? config.offsetRight || "0px" 
      : config.offsetRightMobile || "0px";
  }

  setSize(isOpen, isGreetingMessage = false) {
    const sizeConfig = CONFIG.WIDGET_SIZES[this.config.widgetSize] || CONFIG.WIDGET_SIZES.normal;
    
    if (isOpen) {
      this.setOpenSize(sizeConfig);
    } else {
      this.setClosedSize(isGreetingMessage);
    }
  }

  setOpenSize(sizeConfig) {
    this.wrapper.style.width = `min(100%, ${sizeConfig.width})`;
    this.iframe.style.width = `min(100%, ${sizeConfig.width})`;
    this.wrapper.style.height = `min(100%, ${sizeConfig.height})`;
  }

  setClosedSize(isGreetingMessage) {
    if (isGreetingMessage) {
      this.wrapper.style.width = "280px";
      this.wrapper.style.height = "140px";
    } else {
      const sizes = CONFIG.DEFAULT_SIZES.buttonSizes;
      const size = sizes[this.config.widgetButtonSize] || sizes.default;
      
      this.wrapper.style.height = size.height;
      this.wrapper.style.width = size.width;
    }
  }
}

// Path Matcher
class PathMatcher {
  constructor(config) {
    this.ignorePaths = config.dataIgnorePaths?.split(",") || [];
    this.showPaths = config.dataShowPaths?.split(",") || [];
  }

  shouldAppendIframe() {
    if (!this.ignorePaths.length && !this.showPaths.length) {
      return true;
    }

    return this.checkPathMatches();
  }

  checkPathMatches() {
    const currentUrl = this.normalizeUrl(window.location.href);

    for (const path of this.ignorePaths) {
      if (this.matchPath(path, currentUrl)) {
        return false;
      }
    }

    for (const path of this.showPaths) {
      if (this.matchPath(path, currentUrl)) {
        return true;
      }
    }

    return !this.showPaths.length;
  }

  matchPath(pattern, url) {
    const normalizedPattern = this.normalizeUrl(pattern);
    const isWildcard = normalizedPattern.endsWith('*');

    if (isWildcard) {
      const basePath = normalizedPattern.slice(0, -1);
      return url.startsWith(basePath);
    }

    return normalizedPattern === url;
  }

  normalizeUrl(url) {
    return url.endsWith("/") ? url.slice(0, -1) : url;
  }
}

// Main Initialization
class EBuddyInitializer {
  constructor() {
    this.config = WidgetConfigExtractor.extract();
    this.renderer = new WidgetRenderer(this.config);
    this.pathMatcher = new PathMatcher(this.config);
  }

  init() {
    this.setupMessageListener();
    this.initializeWidget();
  }

  setupMessageListener() {
    window.addEventListener("message", this.handleMessage.bind(this));
  }

  handleMessage(event) {
    if (event.origin !== this.config.ebuddyAddress) return;

    const { type, data } = event.data;

    const messageHandlers = {
      "CONVERSATION_STARTED": () => 
        SessionManager.saveSessionData({
          conversationId: data.conversationId,
          chatbotId: data.chatbotId,
          startedAt: new Date().toISOString(),
        }),
      "CONVERSATION_ENDED": SessionManager.clearSessionData,
      "CHAT_WINDOW_OPENED": () => this.renderer.setSize(true),
      "CHAT_WINDOW_CLOSED": () => this.renderer.setSize(false, true),
      "SHOW_GREETING_MESSAGE": () => this.renderer.setSize(false, true),
      "ERROR": () => logger.error("Chatbot error:", data)
    };

    const handler = messageHandlers[type];
    if (handler) handler();
  }

  initializeWidget() {
    if (this.pathMatcher.shouldAppendIframe()) {
      this.renderer.render();
      this.renderer.wrapper.appendChild(this.renderer.iframe);
      this.renderer.setSize(false, true);
    }
  }
}

// Launch the widget
document.addEventListener('DOMContentLoaded', () => {
  const initializer = new EBuddyInitializer();
  initializer.init();
});