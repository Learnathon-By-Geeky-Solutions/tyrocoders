console.log("loaded embed_mechanims.js");

// Session management functions
const SESSION_KEY = "ebuddy_session";

const getSessionData = () => {
  try {
    const session = localStorage.getItem(SESSION_KEY);
    return session ? JSON.parse(session) : null;
  } catch (error) {
    console.error("Error reading session:", error);
    return null;
  }
};

const saveSessionData = (data) => {
  try {
    // Merge with existing session data instead of replacing
    const existingSession = getSessionData() || {};
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
    localStorage.setItem(SESSION_KEY, JSON.stringify(updatedSession));
  } catch (error) {
    console.error("Error saving session:", error);
  }
};

const clearSessionData = () => {
  try {
    localStorage.removeItem(SESSION_KEY);
  } catch (error) {
    console.error("Error clearing session:", error);
  }
};

const removeHttp = (url) => {
  if (url === undefined) {
    return "";
  }

  return url.replace(/^https?:\/\//, "");
};

const ebuddyScript = document.querySelector(
  "script[data-name='ebuddy']"
);

const offsetBottom = ebuddyScript?.getAttribute(
  "data-widget-offset-bottom"
);
const offsetRight = ebuddyScript?.getAttribute(
  "data-widget-offset-right"
);
const offsetBottomMobile = ebuddyScript?.getAttribute(
  "data-widget-offset-bottom-mobile"
);
const offsetRightMobile = ebuddyScript?.getAttribute(
  "data-widget-offset-right-mobile"
);
const placement = ebuddyScript?.getAttribute("data-placement") || "right";
let chatbotId = ebuddyScript?.getAttribute("data-chatbot-id");
let dataUserId = ebuddyScript?.getAttribute("data-user-id");
const ebuddyAddress = ebuddyScript?.getAttribute("data-address");
const dataIgnorePaths = ebuddyScript?.getAttribute("data-ignore-paths");
const dataShowPaths = ebuddyScript?.getAttribute("data-show-paths");
const dataMovable = ebuddyScript?.getAttribute("data-movable");
let widgetSize = ebuddyScript?.getAttribute("data-widget-size");
let widgetButtonSize = ebuddyScript?.getAttribute(
  "data-widget-button-size"
);

// ================================================

// Create and configure wrapper
const ebuddyWrapper = document.createElement("div");
ebuddyWrapper.id = "ebuddy-wrapper";
ebuddyWrapper.style.zIndex = "9249299";
// ebuddyWrapper.style.height = "100%";
ebuddyWrapper.style.background = "transparent";
ebuddyWrapper.style.overflow = "hidden";
ebuddyWrapper.style.position = "fixed";
ebuddyWrapper.style.bottom = "0px";

function setWrapperPosition() {
  if (placement === "right") {
    ebuddyWrapper.style.right = "0px";
  } else {
    ebuddyWrapper.style.left = "0px";
  }
}

setWrapperPosition();
ebuddyWrapper.style.height =
  widgetButtonSize === "extraLarge" ?
  "110px" :
  widgetButtonSize === "large" ?
  "100px" :
  "90px";
ebuddyWrapper.style.width =
  widgetButtonSize === "extraLarge" ?
  "110px" :
  widgetButtonSize === "large" ?
  "100px" :
  "90px";
const VALID_WIDGET_SIZES = {
  small: {
    height: "680px",
    width: "384px",
  },
  normal: {
    height: "800px",
    width: "440px",
  },
  large: {
    height: "820px",
    width: "572px",
  },
};

if (!VALID_WIDGET_SIZES[widgetSize]) {
  widgetSize = "normal";
}
// Desktop
if (window.matchMedia("(min-width: 800px)").matches) {
  if (offsetBottom) {
    ebuddyWrapper.style.marginBottom = offsetBottom;
  }
  if (offsetRight) {
    ebuddyWrapper.style.marginRight = offsetRight;
  }
  // Set height and width based on widget size
  const widgetSizeConfig =
    VALID_WIDGET_SIZES[widgetSize] || VALID_WIDGET_SIZES["normal"];
} else {
  /* Mobile */
  if (offsetBottomMobile) {
    ebuddyWrapper.style.marginBottom = offsetBottomMobile;
  }
  if (offsetRightMobile) {
    ebuddyWrapper.style.marginRight = offsetRightMobile;
  }
  // Set height and width based on widget size
  const widgetSizeConfig =
    VALID_WIDGET_SIZES[widgetSize] || VALID_WIDGET_SIZES["normal"];
}

document.body.appendChild(ebuddyWrapper);

const iframe = document.createElement("iframe");

function getIframeUrl(chatbotId) {
  let iframeUrl = `${
  window.location.protocol === "https:" ? "https" : "http"
  }://${removeHttp(ebuddyAddress)}/widget/${chatbotId}`;
  const urlObj = new URL(iframeUrl);
  const ebuddyParams = new URLSearchParams();

  // Get existing session
  const session = getSessionData();
  if (session?.conversations?.length > 0) {
    // Get the most recent conversation for this chatbot
    const lastConversation = session.conversations
      .filter((conv) => conv.chatbotId === chatbotId)
      .pop();
    if (lastConversation) {
      ebuddyParams.append(
        "ebuddy_conversation_id",
        lastConversation.conversationId
      );
    }
  }

  if (dataUserId) ebuddyParams.append("dataUserId", dataUserId);
  if (offsetBottom) ebuddyParams.append("offsetBottom", offsetBottom);
  if (offsetRight) ebuddyParams.append("offsetRight", offsetRight);
  if (offsetBottomMobile)
    ebuddyParams.append("offsetBottomMobile", offsetBottomMobile);
  if (offsetRightMobile)
    ebuddyParams.append("offsetRightMobile", offsetRightMobile);
  if (placement) ebuddyParams.append("placement", placement);
  if (chatbotId) ebuddyParams.append("chatbotId", chatbotId);
  if (ebuddyAddress) ebuddyParams.append("address", ebuddyAddress);
  if (dataIgnorePaths)
    ebuddyParams.append("ignorePaths", dataIgnorePaths);
  if (dataShowPaths) ebuddyParams.append("showPaths", dataShowPaths);
  if (dataMovable) ebuddyParams.append("movable", dataMovable);
  if (widgetSize) ebuddyParams.append("widgetSize", widgetSize);
  if (widgetButtonSize)
    ebuddyParams.append("widgetButtonSize", widgetButtonSize);

  urlObj.search = ebuddyParams.toString();

  iframeUrl = urlObj.toString();
  return iframeUrl;
}

let iframeUrl = getIframeUrl(chatbotId);

iframe.setAttribute("src", iframeUrl);
iframe.setAttribute("frameborder", "0");
iframe.setAttribute("scrolling", "no");
iframe.setAttribute(
  "allow",
  "fullscreen; clipboard-read; clipboard-write"
);
iframe.style.width = "100%";
iframe.style.height = "100%";
iframe.style.background = "transparent";
iframe.style.minHeight = "auto";
iframe.style.colorScheme = "light";

iframe.id = "ebuddy";
iframe.style.pointerEvents = "auto";
// Set default iframe and wrapper sizes
function setWrapperAndIframeSize(isOpen, isGreetingMessage = false) {
  const widgetSizeConfig =
    VALID_WIDGET_SIZES[widgetSize] || VALID_WIDGET_SIZES["normal"];

  if (isOpen) {
    // Set the wrapper and iframe width based on the widget size when open
    ebuddyWrapper.style.width = `min(100%, ${widgetSizeConfig.width})`;
    iframe.style.width = `min(100%, ${widgetSizeConfig.width})`;
    ebuddyWrapper.style.height = `min(100%, ${widgetSizeConfig.height})`;
  } else {
    if (isGreetingMessage) {
      // Set the height and width when greeting message is displayed
      ebuddyWrapper.style.width = "280px";
      ebuddyWrapper.style.height = "140px";
    } else {
      // Reset to minimal width when closed and no greeting message
      ebuddyWrapper.style.height =
        widgetButtonSize === "extraLarge" ?
        "110px" :
        widgetButtonSize === "large" ?
        "100px" :
        "90px";
      ebuddyWrapper.style.width =
        widgetButtonSize === "extraLarge" ?
        "110px" :
        widgetButtonSize === "large" ?
        "100px" :
        "90px";
    }
  }
}

function shouldAppendIframe() {
  if (!dataIgnorePaths && !dataShowPaths) {
    if (!document.getElementById("ebuddy")) {
      ebuddyWrapper.appendChild(iframe);
    }
  } else {
    let paths = [];
    if (dataIgnorePaths) {
      paths = dataIgnorePaths.split(",");
    } else if (dataShowPaths) {
      paths = dataShowPaths.split(",");
    }

    let pathMatch = false;
    for (let path of paths) {
      if (path.endsWith("*")) {
        const trimmedPath = path.slice(0, path.length - 2);
        const href = window.location.href;
        if (
          dataIgnorePaths ?
          href.startsWith(trimmedPath) :
          !href.startsWith(trimmedPath)
        ) {
          const iframeToRemove = document.getElementById("ebuddy");
          if (iframeToRemove) {
            iframeToRemove.remove();
            ebuddyWrapper.style.zIndex = "-9249299";
          }
          return;
        }
      } else {
        if (path.endsWith("/")) {
          path = path.slice(0, path.length - 1);
        }
        let url = window.location.href;
        if (url.endsWith("/")) {
          url = url.slice(0, url.length - 1);
        }

        if (dataIgnorePaths && path === url) {
          const iframeToRemove = document.getElementById("ebuddy");
          if (iframeToRemove) {
            iframeToRemove.remove();
            ebuddyWrapper.style.zIndex = "-9249299";
          }
          return;
        }

        if (dataShowPaths && path === url) {
          pathMatch = true;
        }
      }
    }

    if (!pathMatch && dataShowPaths) {
      const iframeToRemove = document.getElementById("ebuddy");
      if (iframeToRemove) {
        iframeToRemove.remove();
        ebuddyWrapper.style.zIndex = "-9249299";
      }
      return;
    }

    if (!document.getElementById("ebuddy")) {
      ebuddyWrapper.appendChild(iframe);
    }
  }
}
// Add this before shouldAppendIframe()
window.addEventListener("message", function(event) {
  // Verify origin
  if (event.origin !== ebuddyAddress) return;

  const {
    type,
    data
  } = event.data;

  switch (type) {
    case "CONVERSATION_STARTED":
      // Save new conversation data
      saveSessionData({
        conversationId: data.conversationId,
        chatbotId: data.chatbotId,
        startedAt: new Date().toISOString(),
      });
      break;

    case "CONVERSATION_ENDED":
      // Clear session when conversation ends
      clearSessionData();
      break;
    case "CHAT_WINDOW_OPENED":
      // Adjust width when chat window opens
      setWrapperAndIframeSize(true);
      break;

    case "CHAT_WINDOW_CLOSED":
      // Collapse width when chat window closes
      setWrapperAndIframeSize(false, true);
      break;
    case "SHOW_GREETING_MESSAGE":
      // Adjust size when greeting message is shown
      setWrapperAndIframeSize(false, true);
      break;
    case "ERROR":
      console.error("Chatbot error:", data);
      break;
  }
});

// Initialize to closed state on load
setWrapperAndIframeSize(false, true);

// Load iframe when appropriate
shouldAppendIframe();