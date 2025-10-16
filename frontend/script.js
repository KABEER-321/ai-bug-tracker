async function submitBug() {
    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;
    const result = document.getElementById("result");

    try {
        const res = await fetch("http://127.0.0.1:5000/bugs", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, description })
        });

        const data = await res.json();

        if (res.ok) {
            alert(data.message);
            result.innerText = "AI Summary: " + data.summary;
        } else {
            alert("Error submitting bug: " + data.error);
        }

    } catch (err) {
        alert("Error submitting bug: " + err);
    }
}
