// document.addEventListener("DOMContentLoaded", () => {
//     const toggleBtn = document.getElementById("toggle-btn");
//     const statusBadge = document.getElementById("status-badge");
//     const metricsPanel = document.getElementById("metrics-panel");
//     const predictionText = document.getElementById("prediction-text");
//     const confidenceFill = document.getElementById("confidence-fill");
//     const confidenceText = document.getElementById("confidence-text");
//     const signalsContainer = document.getElementById("signals-container");
//     const signalsList = document.getElementById("signals-list");

//     // Load current state from storage
//     chrome.storage.local.get(["isScanning"], (result) => {
//         const isScanning = result.isScanning || false;
//         updateUIState(isScanning);
//     });

//     // Toggle button click listener
//     toggleBtn.addEventListener("click", () => {
//         chrome.storage.local.get(["isScanning"], (result) => {
//             const newState = !result.isScanning;
//             chrome.storage.local.set({ isScanning: newState });
//             updateUIState(newState);

//             // Send message to the active tab's content.js
//             chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
//                 if (tabs[0]) {
//                     chrome.tabs.sendMessage(tabs[0].id, {
//                         action: "toggle_scan",
//                         state: newState
//                     });
//                 }
//             });
//         });
//     });

//     function updateUIState(isScanning) {
//         if (isScanning) {
//             toggleBtn.textContent = "Stop Scanning";
//             toggleBtn.className = "btn-stop";
//             statusBadge.textContent = "ON";
//             statusBadge.className = "badge on";
//             metricsPanel.classList.remove("hidden");
//         } else {
//             toggleBtn.textContent = "Start Scanning";
//             toggleBtn.className = "btn-start";
//             statusBadge.textContent = "OFF";
//             statusBadge.className = "badge off";
//             metricsPanel.classList.add("hidden");
//         }
//     }

//     // Listen for analysis results coming back from content.js
//     // Listen for analysis results coming back from content.js
//     chrome.runtime.onMessage.addListener((message) => {
//         if (message.action === "update_metrics" && message.data) {
//             const data = message.data;

//             predictionText.textContent = data.prediction;

//             // Calculate dual confidence scores
//             let fakeConfidence = 0;
//             let realConfidence = 0;

//             if (data.is_fake) {
//                 fakeConfidence = data.confidence * 100;
//                 realConfidence = 100 - fakeConfidence;
//                 predictionText.style.color = "#ff7b72";
//             } else {
//                 realConfidence = data.confidence * 100;
//                 fakeConfidence = 100 - realConfidence;
//                 predictionText.style.color = "#2ea043";
//             }

//             // Update the Real bar
//             document.getElementById("real-text").textContent = `${realConfidence.toFixed(1)}%`;
//             document.getElementById("real-fill").style.width = `${realConfidence}%`;

//             // Update the Fake bar
//             document.getElementById("fake-text").textContent = `${fakeConfidence.toFixed(1)}%`;
//             document.getElementById("fake-fill").style.width = `${fakeConfidence}%`;

//             // Show signals if fake
//             if (data.is_fake && data.signals && data.signals.length > 0) {
//                 signalsContainer.classList.remove("hidden");
//                 signalsList.innerHTML = "";
//                 data.signals.forEach(signal => {
//                     const li = document.createElement("li");
//                     li.textContent = signal;
//                     signalsList.appendChild(li);
//                 });
//             } else {
//                 signalsContainer.classList.add("hidden");
//             }
//         }
//     });
// });
document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("toggle-btn");
    const statusBadge = document.getElementById("status-badge");
    const metricsPanel = document.getElementById("metrics-panel");
    const predictionText = document.getElementById("prediction-text");
    const signalsContainer = document.getElementById("signals-container");
    const signalsList = document.getElementById("signals-list");

    // Load current state from storage
    chrome.storage.local.get(["isScanning"], (result) => {
        const isScanning = result.isScanning || false;
        updateUIState(isScanning);
    });

    // Toggle button click listener
    toggleBtn.addEventListener("click", () => {
        chrome.storage.local.get(["isScanning"], (result) => {
            const newState = !result.isScanning;
            chrome.storage.local.set({ isScanning: newState });
            updateUIState(newState);

            // Send message to the active tab's content.js
            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                if (tabs[0]) {
                    chrome.tabs.sendMessage(tabs[0].id, {
                        action: "toggle_scan",
                        state: newState
                    });
                }
            });
        });
    });

    function updateUIState(isScanning) {
        if (isScanning) {
            toggleBtn.textContent = "Stop Scanning";
            toggleBtn.className = "btn-stop";
            statusBadge.textContent = "ON";
            statusBadge.className = "badge on";
            metricsPanel.classList.remove("hidden");
        } else {
            toggleBtn.textContent = "Start Scanning";
            toggleBtn.className = "btn-start";
            statusBadge.textContent = "OFF";
            statusBadge.className = "badge off";
            metricsPanel.classList.add("hidden");
        }
    }

    // Listen for analysis results coming back from content.js
    chrome.runtime.onMessage.addListener((message) => {
        if (message.action === "update_metrics" && message.data) {
            const data = message.data;

            predictionText.textContent = data.prediction;

            // Calculate dual confidence scores
            let fakeConfidence = 0;
            let realConfidence = 0;

            if (data.is_fake) {
                fakeConfidence = data.confidence * 100;
                realConfidence = 100 - fakeConfidence;
                predictionText.style.color = "#ff7b72";
            } else {
                realConfidence = data.confidence * 100;
                fakeConfidence = 100 - realConfidence;
                predictionText.style.color = "#2ea043";
            }

            // Update the Real bar
            document.getElementById("real-text").textContent = `${realConfidence.toFixed(1)}%`;
            document.getElementById("real-fill").style.width = `${realConfidence}%`;

            // Update the Fake bar
            document.getElementById("fake-text").textContent = `${fakeConfidence.toFixed(1)}%`;
            document.getElementById("fake-fill").style.width = `${fakeConfidence}%`;

            // Show signals if fake
            if (data.is_fake && data.signals && data.signals.length > 0) {
                signalsContainer.classList.remove("hidden");
                signalsList.innerHTML = "";
                data.signals.forEach(signal => {
                    const li = document.createElement("li");
                    li.textContent = signal;
                    signalsList.appendChild(li);
                });
            } else {
                signalsContainer.classList.add("hidden");
            }
        }
    });
});