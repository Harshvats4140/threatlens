document.addEventListener("DOMContentLoaded", async () => {
  const siteEl = document.getElementById("site");
  const statusEl = document.getElementById("status");
  const riskEl = document.getElementById("riskScore");
  const button = document.getElementById("checkBtn");

  let currentURL = "";

  // 🔹 Get current tab URL
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  currentURL = tab.url;

  // 🔹 Display shortened URL
  let displayURL = currentURL;
  if (displayURL.length > 50) {
    displayURL = displayURL.slice(0, 50) + " ...";
  }
  siteEl.innerText = displayURL;

  // 🔥 MAIN SCAN FUNCTION (reusable)
  async function scanURL() {
    statusEl.innerText = "🔄 Scanning...";
    statusEl.style.color = "white";
    riskEl.innerText = "";

    try {
      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ url: currentURL })
      });

      const data = await response.json();

      // ❌ If backend error
      if (data.error) {
        statusEl.innerText = "❌ " + data.error;
        statusEl.style.color = "red";
        return;
      }

      // ✅ RESULT DISPLAY
      if (data.result === "Safe") {
        statusEl.innerText = "✅ Safe Website";
        statusEl.style.color = "green";
      } 
      else if (data.result === "Suspicious") {
        statusEl.innerText = "⚠️ Suspicious Website";
        statusEl.style.color = "orange";
      } 
      else {
        statusEl.innerText = "❌ Malicious Website";
        statusEl.style.color = "red";
      }

      // 📊 Risk Score
      if (data.risk_score !== undefined && data.risk_score !== null) {
        riskEl.innerText = `Risk Score: ${data.risk_score}%`;
      }

      // 🔥 Show reason (NEW 🔥)
      if (data.reason) {
        riskEl.innerText += `\nReason: ${data.reason}`;
      }

      // 🔥 Extra intelligence (NEW 🔥)
      if (data.domain_age_days !== undefined && data.domain_age_days !== null) {
        riskEl.innerText += `\nDomain Age: ${data.domain_age_days} days`;
      }

      if (data.entropy !== undefined && data.entropy !== null) {
        riskEl.innerText += `\nEntropy: ${data.entropy}`;
      }

    } catch (error) {
      statusEl.innerText = "❌ Server not reachable";
      statusEl.style.color = "red";
      riskEl.innerText = "Make sure Flask server is running";
      console.error(error);
    }
  }

  // 🔘 Button click
  button.addEventListener("click", scanURL);

  // 🚀 AUTO SCAN ON OPEN (optional but powerful)
  scanURL();
});