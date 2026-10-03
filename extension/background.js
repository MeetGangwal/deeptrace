// Listens for installation and sets default state
chrome.runtime.onInstalled.addListener(() => {
    chrome.storage.local.set({ isScanning: false });
    console.log("DeepTrace initialized.");
});