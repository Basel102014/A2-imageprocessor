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

    // repopulate dropdown after upload
    await populateFileDropdown();
  } finally {
    hideSpinner();
  }
}

async function processFile() {
  const filename = document.getElementById("process-file").value;

  if (!filename) {
    alert("Please select a file to process.");
    return;
  }

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
  const filename = document.getElementById("stress-file").value;
  const duration = parseInt(document.getElementById("duration").value, 10);

  if (!filename) {
    alert("Please select a file to run the stress test on.");
    return;
  }

  showSpinner();
  const res = await fetch("/process/stress", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + getToken()
    },
    body: JSON.stringify({ filename, duration })
  });
  const data = await res.json();
  hideSpinner();

  alert(`Stress Test Results: ${data.iterations} iterations on ${filename}`);
}

async function populateFileDropdown() {
  const stressSelect = document.getElementById("stress-file");
  const processSelect = document.getElementById("process-file");

  try {
    const res = await fetch("/upload/list", {
      headers: { "Authorization": "Bearer " + getToken() }
    });
    const data = await res.json();

    // Clear both
    if (stressSelect) stressSelect.innerHTML = "";
    if (processSelect) processSelect.innerHTML = "";

    if (!data.uploads || data.uploads.length === 0) {
      const option = document.createElement("option");
      option.disabled = true;
      option.selected = true;
      option.textContent = "No files available";

      if (stressSelect) stressSelect.appendChild(option.cloneNode(true));
      if (processSelect) processSelect.appendChild(option.cloneNode(true));
      return;
    }

    data.uploads.forEach(file => {
      const option = document.createElement("option");
      option.value = file.filename;
      const resolutionText = file.resolution ? ` (${file.resolution})` : "";
      option.textContent = `${file.filename}${resolutionText}`;

      if (stressSelect) stressSelect.appendChild(option.cloneNode(true));
      if (processSelect) processSelect.appendChild(option.cloneNode(true));
    });
  } catch (err) {
    console.error("Failed to load files:", err);
  }
}

let allResults = [];
let currentPage = 1;
const resultsPerPage = 5;
let sortColumn = "timestamp";
let sortDirection = "asc";

async function viewResults() {
  showSpinner();
  const res = await fetch("/results/metadata", {
    headers: { "Authorization": "Bearer " + getToken() }
  });
  const data = await res.json();
  hideSpinner();

  allResults = data.metadata || [];

  sortResults("timestamp");

  currentPage = 1;
  renderResultsPage();
}

function renderResultsPage() {
  const resultsDiv = document.getElementById("results");
  const paginationDiv = document.getElementById("pagination");

  const start = (currentPage - 1) * resultsPerPage;
  const end = start + resultsPerPage;
  const pageResults = allResults.slice(start, end);

    let html = `
    <table class="results-table">
        <thead>
        <tr>
            <th onclick="sortResults('user')">User${getSortIndicator("user")}</th>
            <th onclick="sortResults('input')">Input${getSortIndicator("input")}</th>
            <th onclick="sortResults('output')">Output${getSortIndicator("output")}</th>
            <th onclick="sortResults('timestamp')">Time${getSortIndicator("timestamp")}</th>
            <th>Preview</th>
        </tr>
        </thead>
        <tbody>
    `;

  pageResults.forEach(r => {
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
  resultsDiv.innerHTML = html;
	const totalPages = Math.ceil(allResults.length / resultsPerPage);
	paginationDiv.innerHTML = "";

	if (totalPages > 1) {
	const prevBtn = document.createElement("button");
	prevBtn.textContent = "Prev";
	prevBtn.disabled = currentPage === 1;
	prevBtn.onclick = () => {
			if (currentPage > 1) {
			currentPage--;
			renderResultsPage();
			}
	};
	paginationDiv.appendChild(prevBtn);

	for (let i = 1; i <= totalPages; i++) {
			const btn = document.createElement("button");
			btn.textContent = i;
			if (i === currentPage) btn.classList.add("active");
			btn.onclick = () => {
			currentPage = i;
			renderResultsPage();
			};
			paginationDiv.appendChild(btn);
	}

	const nextBtn = document.createElement("button");
	nextBtn.textContent = "Next";
	nextBtn.disabled = currentPage === totalPages;
	nextBtn.onclick = () => {
			if (currentPage < totalPages) {
			currentPage++;
			renderResultsPage();
			}
	};
	paginationDiv.appendChild(nextBtn);
	}
}

function sortResults(column) {
  if (sortColumn === column) {
    sortDirection = sortDirection === "asc" ? "desc" : "asc";
  } else {
    sortColumn = column;
    sortDirection = "asc";
  }

  allResults.sort((a, b) => {
    let valA = a[column];
    let valB = b[column];

    if (column === "timestamp") {
      valA = new Date(valA);
      valB = new Date(valB);
    }

    if (valA < valB) return sortDirection === "asc" ? -1 : 1;
    if (valA > valB) return sortDirection === "asc" ? 1 : -1;
    return 0;
  });

  currentPage = 1;
  renderResultsPage();
}

function getSortIndicator(column) {
  if (sortColumn === column) {
    return sortDirection === "asc" ? " ▲" : " ▼";
  }
  return " ⇅";
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
  const onDashboard = document.getElementById("results") !== null;
  if (onDashboard && !getToken()) {
    window.location.href = "/login";
  }

  if (onDashboard) {
    populateFileDropdown();
  }
});
