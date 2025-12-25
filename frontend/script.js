const API_BASE = "https://ai-bug-tracker-obl1.onrender.com";

// Helper: Get or Create Unique Device ID
function getDeviceId() {
    let deviceId = localStorage.getItem("bug_tracker_device_id");
    if (!deviceId) {
        // Generate a random ID (simple implementation)
        deviceId = "user_" + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
        localStorage.setItem("bug_tracker_device_id", deviceId);
    }
    return deviceId;
}

document.addEventListener("DOMContentLoaded", () => {
    fetchBugs();
});

async function fetchBugs() {
    const bugsList = document.getElementById("bugs-list");
    try {
        const deviceId = getDeviceId();
        const response = await fetch(`${API_BASE}/bugs?user_id=${deviceId}`);
        const bugs = await response.json();

        bugsList.innerHTML = ""; // Clear existing

        if (bugs.length === 0) {
            bugsList.innerHTML = `<p style="text-align: center; color: var(--text-muted);">No bugs reported yet. Be the first!</p>`;
            return;
        }

        bugsList.innerHTML = bugs.reverse().map(bug => `
            <div class="bug-item">
                <div class="bug-header">
                    <span class="bug-title">${escapeHTML(bug.title)}</span>
                    <span class="status-badge">${bug.status}</span>
                </div>
                <p class="bug-desc">${escapeHTML(bug.description)}</p>
                <div class="summary-box">
                    <div class="summary-label">Technical Solution</div>
                    <div class="markdown-content">${marked.parse(bug.summary)}</div>
                </div>
            </div>
        `).join("");
    } catch (err) {
        listElement.innerHTML = `<p style="text-align: center; color: #ef4444;">Failed to load bugs. Is the server running?</p>`;
    }
}

async function submitBug() {
    const titleInput = document.getElementById("title");
    const descInput = document.getElementById("description");
    const submitBtn = document.getElementById("submit-btn");

    const title = titleInput.value.trim();
    const description = descInput.value.trim();

    if (!title || !description) {
        alert("Please fill in both title and description.");
        return;
    }

    // UI Feedback
    const originalBtnContent = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<div class="loading-spinner"></div> <span>Asking Gemini for Solution...</span>`;

    try {
        const deviceId = getDeviceId();
        const res = await fetch(`${API_BASE}/bugs`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                title,
                description,
                user_id: deviceId
            })
        });

        const data = await res.json();

        if (res.ok) {
            titleInput.value = "";
            descInput.value = "";
            await fetchBugs();
        } else {
            alert("Error: " + data.error);
        }

    } catch (err) {
        alert("Server connection failed. Please ensure the backend is running.");
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnContent;
    }
}

function escapeHTML(str) {
    const p = document.createElement("p");
    p.textContent = str;
    return p.innerHTML;
}
