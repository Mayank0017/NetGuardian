

  document.getElementById('closeTab').addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: "close_popup", senderTabId: chrome.runtime.id });
    window.close();
  });
  
  document.getElementById('continue').addEventListener('click', () => {
    window.close();
  });