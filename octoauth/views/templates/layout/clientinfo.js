function guessNavigator() {
  const userAgent = navigator.userAgent;
  let match =
    userAgent.match(
      /(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i
    ) || [];
  let temp;

  if (/trident/i.test(match[1])) {
    temp = /\brv[ :]+(\d+)/g.exec(userAgent) || [];

    return "IE " + (temp[1] || "");
  }

  if (match[1] === "Chrome") {
    temp = userAgent.match(/\b(OPR|Edge)\/(\d+)/);

    if (temp !== null) {
      return temp.slice(1).join(" ").replace("OPR", "Opera");
    }

    temp = userAgent.match(/\b(Edg)\/(\d+)/);

    if (temp !== null) {
      return temp.slice(1).join(" ").replace("Edg", "Edge (Chromium)");
    }
  }

  match = match[2]
    ? [match[1], match[2]]
    : [navigator.appName, navigator.appVersion, "-?"];
  temp = userAgent.match(/version\/(\d+)/i);

  if (temp !== null) {
    match.splice(1, 1, temp[1]);
  }

  return match.join(" ");
}

function guessPlatform() {
  if (window.navigator.userAgent.indexOf("Windows NT 10.0") != -1)
    return "Windows 10";
  if (window.navigator.userAgent.indexOf("Windows NT 6.3") != -1)
    return "Windows 8.1";
  if (window.navigator.userAgent.indexOf("Windows NT 6.2") != -1)
    return "Windows 8";
  if (window.navigator.userAgent.indexOf("Windows NT 6.1") != -1)
    return "Windows 7";
  if (window.navigator.userAgent.indexOf("Windows NT 6.0") != -1)
    return "Windows Vista";
  if (window.navigator.userAgent.indexOf("Windows NT 5.1") != -1)
    return "Windows XP";
  if (window.navigator.userAgent.indexOf("Windows NT 5.0") != -1)
    return "Windows 2000";
  if (window.navigator.userAgent.indexOf("Mac") != -1) return "Mac/iOS";
  if (window.navigator.userAgent.indexOf("Linux") != -1) return "Linux";
  if (window.navigator.userAgent.indexOf("X11") != -1) return "UNIX";

  return null;
}

function setClientInfo() {
  document.querySelector("input[name=browser]").value = guessNavigator();
  document.querySelector("input[name=platform]").value = guessPlatform();
}
