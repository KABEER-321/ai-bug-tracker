const API_BASE = "http://127.0.0.1:5000";

document.addEventListener("DOMContentLoaded", () => {
    fetchBugs();
});

async function fetchBugs() {
    const listElement = document.getElementById("bugs-list");
    try {
        const res = await fetch(`${API_BASE}/bugs`);
        const bugs = await res.json();

        if (bugs.length === 0) {
            listElement.innerHTML = `<p style="text-align: center; color: var(--text-muted);">No bugs reported yet. Be the first!</p>`;
            return;
        }

        listElement.innerHTML = bugs.reverse().map(bug => `
            <div class="bug-item">
                <div class="bug-header">
                    <span class="bug-title">${escapeHTML(bug.title)}</span>
                    <span class="status-badge">${bug.status}</span>
                </div>
                <p class="bug-desc">${escapeHTML(bug.description)}</p>
                <div class="summary-box">
                    <div class="summary-label">AI Summary</div>
                    <p>${escapeHTML(bug.summary)}</p>
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
    submitBtn.innerHTML = `<div class="loading-spinner"></div> <span>Generating Summary...</span>`;

    try {
        const res = await fetch(`${API_BASE}/bugs`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, description })
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
