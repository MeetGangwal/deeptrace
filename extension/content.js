// let isScanning = false;
// let scanInterval = null;
// let overlayDiv = null;

// // Listen for commands from the popup
// chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
//     if (request.action === "toggle_scan") {
//         isScanning = request.state;
//         if (isScanning) {
//             startScanning();
//         } else {
//             stopScanning();
//         }
//         sendResponse({ status: "acknowledged" });
//     }
// });

// function startScanning() {
//     const video = document.querySelector('video');
//     if (!video) {
//         alert("DeepTrace: No video player found on this page.");
//         return;
//     }

//     createOverlay(video);

//     // Extract a frame every 1.5 seconds to save resources
//     scanInterval = setInterval(() => {
//         analyzeVideoFrame(video);
//     }, 1500);
// }

// function stopScanning() {
//     if (scanInterval) clearInterval(scanInterval);
//     if (overlayDiv) {
//         overlayDiv.remove();
//         overlayDiv = null;
//     }
// }

// function createOverlay(videoElement) {
//     overlayDiv = document.createElement('div');
//     overlayDiv.style.position = 'absolute';
//     overlayDiv.style.border = '2px solid transparent';
//     overlayDiv.style.pointerEvents = 'none'; // Click through it
//     overlayDiv.style.zIndex = '9999';

//     // Match overlay size to video player
//     const rect = videoElement.getBoundingClientRect();
//     overlayDiv.style.top = `${rect.top + window.scrollY}px`;
//     overlayDiv.style.left = `${rect.left + window.scrollX}px`;
//     overlayDiv.style.width = `${rect.width}px`;
//     overlayDiv.style.height = `${rect.height}px`;

//     document.body.appendChild(overlayDiv);
// }

// async function analyzeVideoFrame(video) {
//     // Create hidden canvas to grab the frame pixels
//     const canvas = document.createElement('canvas');
//     canvas.width = video.videoWidth;
//     canvas.height = video.videoHeight;
//     const ctx = canvas.getContext('2d');
//     ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

//     const base64Image = canvas.toDataURL('image/jpeg', 0.8);

//     try {
//         const response = await fetch("http://127.0.0.1:8000/analyze-frame", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({
//                 image_base64: base64Image,
//                 timestamp: video.currentTime
//             })
//         });

//         const data = await response.json();

//         // Auto-pause feature: Trigger if model detects a fake with >80% confidence
//         if (data.is_fake && data.confidence > 0.80) {
//             if (!video.paused) {
//                 video.pause();
//                 alert(`DeepTrace Alert: Video paused. High probability of AI manipulation detected (${(data.confidence * 100).toFixed(1)}%).`);
//             }
//         }

//         updateOverlay(data, video);

//         // Send data to popup to display metrics
//         chrome.runtime.sendMessage({ action: "update_metrics", data: data });

//     } catch (error) {
//         console.error("DeepTrace API Error:", error);
//     }
// }

// function updateOverlay(data, video) {
//     if (!overlayDiv) return;

//     // Clear previous boxes
//     overlayDiv.innerHTML = '';

//     if (data.is_fake && data.face_box) {
//         const scaleX = overlayDiv.offsetWidth / video.videoWidth;
//         const scaleY = overlayDiv.offsetHeight / video.videoHeight;

//         const box = document.createElement('div');
//         box.style.position = 'absolute';
//         box.style.border = '3px solid red';
//         box.style.backgroundColor = 'rgba(255, 0, 0, 0.2)';

//         box.style.left = `${data.face_box.x * scaleX}px`;
//         box.style.top = `${data.face_box.y * scaleY}px`;
//         box.style.width = `${data.face_box.width * scaleX}px`;
//         box.style.height = `${data.face_box.height * scaleY}px`;

//         const label = document.createElement('span');
//         label.innerText = `⚠️ Deepfake (${(data.confidence * 100).toFixed(1)}%)`;
//         label.style.backgroundColor = 'red';
//         label.style.color = 'white';
//         label.style.fontSize = '12px';
//         label.style.fontWeight = 'bold';
//         label.style.position = 'absolute';
//         label.style.top = '-20px';
//         label.style.left = '0';
//         label.style.padding = '2px 4px';

//         box.appendChild(label);
//         overlayDiv.appendChild(box);
//     }
// }
// //----------------NEW-------------------------------
// function showDeepfakeOverlay(confidenceScore, videoElement) {
//     // Prevent creating multiple overlays if one is already active
//     if (document.getElementById('deeptrace-overlay')) return;

//     // Create the main overlay container
//     const overlay = document.createElement('div');
//     overlay.id = 'deeptrace-overlay';

//     // CSS to cover the video player completely
//     overlay.style.position = 'absolute';
//     overlay.style.top = '0';
//     overlay.style.left = '0';
//     overlay.style.width = '100%';
//     overlay.style.height = '100%';
//     overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.85)';
//     overlay.style.backdropFilter = 'blur(4px)';
//     overlay.style.display = 'flex';
//     overlay.style.flexDirection = 'column';
//     overlay.style.justifyContent = 'center';
//     overlay.style.alignItems = 'center';
//     overlay.style.zIndex = '999999';
//     overlay.style.fontFamily = 'Arial, sans-serif';
//     overlay.style.color = 'white';

//     // Add the warning title
//     const title = document.createElement('h1');
//     title.innerText = '⚠️ DeepTrace Alert';
//     title.style.color = '#ff4d4d';
//     title.style.margin = '0 0 10px 0';

//     // Add the confidence score text
//     const subtitle = document.createElement('p');
//     subtitle.innerText = `Video paused. High probability of AI manipulation detected (${confidenceScore}%).`;
//     subtitle.style.fontSize = '18px';

//     // Add the 'Resume Video' button
//     const resumeBtn = document.createElement('button');
//     resumeBtn.innerText = 'I Understand, Resume Video';
//     resumeBtn.style.marginTop = '20px';
//     resumeBtn.style.padding = '12px 24px';
//     resumeBtn.style.fontSize = '16px';
//     resumeBtn.style.fontWeight = 'bold';
//     resumeBtn.style.cursor = 'pointer';
//     resumeBtn.style.backgroundColor = '#ff4d4d';
//     resumeBtn.style.color = 'white';
//     resumeBtn.style.border = 'none';
//     resumeBtn.style.borderRadius = '6px';

//     // When clicked, remove the overlay and play the video
//     resumeBtn.onclick = () => {
//         overlay.remove();
//         videoElement.play();
//     };

//     // Assemble the overlay
//     overlay.appendChild(title);
//     overlay.appendChild(subtitle);
//     overlay.appendChild(resumeBtn);

//     // Inject it directly into the video's parent container
//     videoElement.parentElement.appendChild(overlay);

//     // Pause the video
//     videoElement.pause();
// }

// ---------------------------------------------NEW Code -------------------------------------

let isScanning = false;
let scanInterval = null;
let overlayDiv = null;
let warningPopover = null;

// Listen for commands from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "toggle_scan") {
        isScanning = request.state;
        if (isScanning) {
            startScanning();
        } else {
            stopScanning();
        }
        sendResponse({ status: "acknowledged" });
    }
});

function startScanning() {
    const video = document.querySelector('video');
    if (!video) {
        alert("DeepTrace: No video player found on this page.");
        return;
    }

    createOverlay(video);

    // Extract a frame every 1.5 seconds to save resources
    scanInterval = setInterval(() => {
        analyzeVideoFrame(video);
    }, 1500);
}

function stopScanning() {
    if (scanInterval) clearInterval(scanInterval);
    if (overlayDiv) {
        overlayDiv.remove();
        overlayDiv = null;
    }
    if (warningPopover) {
        warningPopover.remove();
        warningPopover = null;
    }
}

function createOverlay(videoElement) {
    overlayDiv = document.createElement('div');
    overlayDiv.style.position = 'absolute';
    overlayDiv.style.border = '2px solid transparent';
    overlayDiv.style.pointerEvents = 'none'; // Click through it
    overlayDiv.style.zIndex = '9999';

    // Match overlay size to video player
    const rect = videoElement.getBoundingClientRect();
    overlayDiv.style.top = `${rect.top + window.scrollY}px`;
    overlayDiv.style.left = `${rect.left + window.scrollX}px`;
    overlayDiv.style.width = `${rect.width}px`;
    overlayDiv.style.height = `${rect.height}px`;

    document.body.appendChild(overlayDiv);
}

async function analyzeVideoFrame(video) {
    // Create hidden canvas to grab the frame pixels
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const base64Image = canvas.toDataURL('image/jpeg', 0.8);

    try {
        const response = await fetch("http://127.0.0.1:8000/analyze-frame", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                image_base64: base64Image,
                timestamp: video.currentTime
            })
        });

        const data = await response.json();

        // Auto-pause feature: Trigger if model detects a fake with >80% confidence
        if (data.is_fake && data.confidence > 0.80) {
            if (!video.paused) {
                showDeepfakeOverlay((data.confidence * 100).toFixed(1), video);
            }
        }

        updateOverlay(data, video);

        // Send data to popup to display metrics
        chrome.runtime.sendMessage({ action: "update_metrics", data: data });

    } catch (error) {
        console.error("DeepTrace API Error:", error);
    }
}

function updateOverlay(data, video) {
    if (!overlayDiv) return;

    // Clear previous boxes
    overlayDiv.innerHTML = '';

    if (data.is_fake && data.face_box) {
        const scaleX = overlayDiv.offsetWidth / video.videoWidth;
        const scaleY = overlayDiv.offsetHeight / video.videoHeight;

        const box = document.createElement('div');
        box.style.position = 'absolute';
        box.style.border = '3px solid red';
        box.style.backgroundColor = 'rgba(255, 0, 0, 0.2)';

        box.style.left = `${data.face_box.x * scaleX}px`;
        box.style.top = `${data.face_box.y * scaleY}px`;
        box.style.width = `${data.face_box.width * scaleX}px`;
        box.style.height = `${data.face_box.height * scaleY}px`;

        const label = document.createElement('span');
        label.innerText = `⚠️ Deepfake (${(data.confidence * 100).toFixed(1)}%)`;
        label.style.backgroundColor = 'red';
        label.style.color = 'white';
        label.style.fontSize = '12px';
        label.style.fontWeight = 'bold';
        label.style.position = 'absolute';
        label.style.top = '-20px';
        label.style.left = '0';
        label.style.padding = '2px 4px';

        box.appendChild(label);
        overlayDiv.appendChild(box);
    }
}

//----------------NEW (Upgraded with Popover API)-------------------------------
function showDeepfakeOverlay(confidenceScore, videoElement) {
    if (document.getElementById('deeptrace-warning-popover')) return;

    // 1. Create a container using the new top-layer 'popover' attribute
    warningPopover = document.createElement('div');
    warningPopover.id = 'deeptrace-warning-popover';

    // Explicitly set the popover attribute to "manual" so it behaves like a modal
    warningPopover.setAttribute('popover', 'manual');

    // 2. Style the dialog box
    warningPopover.style.padding = '40px';
    warningPopover.style.backgroundColor = '#1a1a1a';
    warningPopover.style.border = '2px solid #ff4d4d';
    warningPopover.style.borderRadius = '12px';
    warningPopover.style.fontFamily = 'Arial, sans-serif';
    warningPopover.style.color = 'white';
    warningPopover.style.textAlign = 'center';
    warningPopover.style.boxShadow = '0px 10px 30px rgba(0,0,0,0.5)';
    warningPopover.style.margin = 'auto'; // Center the popover

    // The ::backdrop handles the dark overlay over the whole screen automatically in the Top Layer
    // We inject a tiny style tag to style the backdrop natively
    const style = document.createElement('style');
    style.textContent = `
        #deeptrace-warning-popover::backdrop {
            background-color: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(4px);
        }
    `;
    warningPopover.appendChild(style);

    // 3. Add content
    const title = document.createElement('h1');
    title.innerText = '⚠️ DeepTrace Alert';
    title.style.color = '#ff4d4d';
    title.style.margin = '0 0 10px 0';

    const subtitle = document.createElement('p');
    subtitle.innerText = `Video paused. High probability of AI manipulation detected (${confidenceScore}%).`;
    subtitle.style.fontSize = '18px';

    const resumeBtn = document.createElement('button');
    resumeBtn.innerText = 'I Understand, Resume Video';
    resumeBtn.style.marginTop = '20px';
    resumeBtn.style.padding = '12px 24px';
    resumeBtn.style.fontSize = '16px';
    resumeBtn.style.fontWeight = 'bold';
    resumeBtn.style.cursor = 'pointer';
    resumeBtn.style.backgroundColor = '#ff4d4d';
    resumeBtn.style.color = 'white';
    resumeBtn.style.border = 'none';
    resumeBtn.style.borderRadius = '6px';

    // 4. Handle interaction
    resumeBtn.onclick = () => {
        warningPopover.hidePopover(); // Native method to close the popover
        warningPopover.remove();
        videoElement.play();
    };

    warningPopover.appendChild(title);
    warningPopover.appendChild(subtitle);
    warningPopover.appendChild(resumeBtn);

    // 5. Append to body and trigger the native top-layer display
    document.body.appendChild(warningPopover);

    // Pause the video and show the popover
    videoElement.pause();
    warningPopover.showPopover(); // Native method to push it into the Top Layer
}