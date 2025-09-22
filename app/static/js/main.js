function showSpinner() {
  document.getElementById("spinner").style.display = "flex";
}

function hideSpinner() {
  document.getElementById("spinner").style.display = "none";
}

function getToken() {
  return localStorage.getItem("token");
}

async function uploadFile(event) {
  event.preventDefault();
  showSpinner();
  const fileInput = document.getElementById("file");
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const res = await fetch("/upload/", {
      method: "POST",
      headers: { "Authorization": "Bearer " + getToken() },
      body: formData
    });
    const data = await res.json();
    alert("Uploaded: " + data.filename);
  } finally {
    hideSpinner();
  }
}

async function processFile() {
  const filename = document.getElementById("filename").value;
  showSpinner();
  const res = await fetch("/process/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + getToken()
    },
    body: JSON.stringify({ filename })
  });
  const data = await res.json();
  hideSpinner();
  alert("Processed: " + data.result);
}

async function stressTest() {
  const filename = document.getElementById("filename").value;
  showSpinner();
  const res = await fetch("/process/stress", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + getToken()
    },
    body: JSON.stringify({ filename, duration: 10 })
  });
  const data = await res.json();
  hideSpinner();
  alert("Stress Test Results: " + data.iterations + " iterations");
}

async function viewResults() {
  showSpinner();
  const res = await fetch("/results/metadata", {
    headers: { "Authorization": "Bearer " + getToken() }
  });
  const data = await res.json();

  let html = `
    <table class="results-table">
      <thead>
        <tr>
          <th>User</th>
          <th>Input</th>
          <th>Output</th>
          <th>Time</th>
          <th>Preview</th>
        </tr>
      </thead>
      <tbody>
  `;

  data.metadata.forEach(r => {
    html += `
      <tr>
        <td>${r.user}</td>
        <td>${r.input}</td>
        <td>${r.output}</td>
        <td>${new Date(r.timestamp).toLocaleString()}</td>
        <td>
          <a href="/results/${r.output}" target="_blank">
            <img src="/results/${r.output}" alt="Processed" class="thumbnail">
          </a>
        </td>
      </tr>
    `;
  });

  html += "</tbody></table>";
  hideSpinner();
  document.getElementById("results").innerHTML = html;
}

function logout() {
  localStorage.removeItem("token");
  window.location.href = "/login";
}

async function login(event) {
  event.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  if (data.token) {
    localStorage.setItem("token", data.token);
    window.location.href = "/dashboard";
  } else {
    alert("Login failed: " + (data.error || "Unknown error"));
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // If the dashboard elements exist but there's no token, bounce to login
  const onDashboard = document.getElementById("results") !== null;
  if (onDashboard && !getToken()) {
    window.location.href = "/login";
  }
});
