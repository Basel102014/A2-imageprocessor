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
    await populateFileDropdown();
  } finally {
    hideSpinner();
  }
}

async function processFile() {
  const filename = document.getElementById("process-file").value;
  if (!filename) return alert("Please select a file to process.");

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

  // Refresh results table with current pagination/sort/filter
  await viewResults(currentPage, sortColumn, sortDirection, currentFilter);
}

async function stressTest() {
  const filename = document.getElementById("stress-file").value;
  const duration = parseInt(document.getElementById("duration").value, 10);
  if (!filename) return alert("Please select a file to run the stress test on.");

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

  // Refresh results table with current pagination/sort/filter
  await viewResults(currentPage, sortColumn, sortDirection, currentFilter);
}

async function populateFileDropdown(page = 1, limit = 50, sort = "filename", order = "asc", filter = "") {
  const stressSelect = document.getElementById("stress-file");
  const processSelect = document.getElementById("process-file");

  try {
    let url = `/upload/list?page=${page}&limit=${limit}&sort=${sort}&order=${order}`;
    if (filter) {
      url += `&q=${encodeURIComponent(filter)}`;
    }

    const res = await fetch(url, {
      headers: { "Authorization": "Bearer " + getToken() }
    });
    const data = await res.json();

    [stressSelect, processSelect].forEach(select => {
      if (!select) return;
      select.innerHTML = "";

      if (!data.results || data.results.length === 0) {
        const option = new Option("No files available", "", true, true);
        option.disabled = true;
        select.appendChild(option);
        return;
      }

      data.results.forEach(file => {
        const resolutionText = file.resolution ? ` (${file.resolution})` : "";
        select.appendChild(new Option(`${file.filename}${resolutionText}`, file.filename));
      });
    });

    console.log(`Page ${data.page} of ${Math.ceil(data.total / data.limit)} (${data.total} files total)`);

  } catch (err) {
    console.error("Failed to load files:", err);
  }
}

// ---------------- Results table ----------------
let currentPage = 1;
const resultsPerPage = 5;
let sortColumn = "timestamp";
let sortDirection = "desc";
let totalPages = 1;
let currentFilter = "";

async function viewResults(page = 1, sort = sortColumn, order = sortDirection, filter = currentFilter) {
  showSpinner();
  let url = `/results/metadata?page=${page}&limit=${resultsPerPage}&sort=${sort}&order=${order}`;
  if (filter) {
    url += `&input=${encodeURIComponent(filter)}`;
  }

  const res = await fetch(url, {
    headers: { "Authorization": "Bearer " + getToken() }
  });
  const data = await res.json();
  hideSpinner();

  currentPage = data.page;
  totalPages = Math.ceil(data.total / resultsPerPage);

  renderResultsPage(data.results);
}

function renderResultsPage(results) {
  const resultsDiv = document.getElementById("results");
  const paginationDiv = document.getElementById("pagination");

  let html = `
    <table class="results-table">
      <thead>
        <tr>
          <th onclick="changeSort('user')">User${getSortIndicator("user")}</th>
          <th onclick="changeSort('input')">Input${getSortIndicator("input")}</th>
          <th onclick="changeSort('output')">Output${getSortIndicator("output")}</th>
          <th onclick="changeSort('timestamp')">Time${getSortIndicator("timestamp")}</th>
          <th>Preview</th>
        </tr>
      </thead>
      <tbody>
  `;

  results.forEach(r => {
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

  paginationDiv.innerHTML = "";
  if (totalPages > 1) {
    const prevBtn = document.createElement("button");
    prevBtn.textContent = "Prev";
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => viewResults(currentPage - 1);
    paginationDiv.appendChild(prevBtn);

    for (let i = 1; i <= totalPages; i++) {
      const btn = document.createElement("button");
      btn.textContent = i;
      if (i === currentPage) btn.classList.add("active");
      btn.onclick = () => viewResults(i);
      paginationDiv.appendChild(btn);
    }

    const nextBtn = document.createElement("button");
    nextBtn.textContent = "Next";
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.onclick = () => viewResults(currentPage + 1);
    paginationDiv.appendChild(nextBtn);
  }
}

function changeSort(column) {
  if (sortColumn === column) {
    sortDirection = sortDirection === "asc" ? "desc" : "asc";
  } else {
    sortColumn = column;
    sortDirection = "asc";
  }
  viewResults(1, sortColumn, sortDirection);
}

function getSortIndicator(column) {
  if (sortColumn === column) {
    return sortDirection === "asc" ? " ▲" : " ▼";
  }
  return " ⇅";
}

function applyFilter() {
  const filterBox = document.getElementById("filter-input");
  currentFilter = filterBox.value.trim();
  viewResults(1, sortColumn, sortDirection, currentFilter);
}

async function clearData() {
  if (!confirm("Are you sure you want to delete all results? This action cannot be undone.")) {
    return;
  }

  const res = await fetch("/results/clear", {
    method: "DELETE",
    headers: { "Authorization": "Bearer " + getToken() }
  });

  if (res.ok) {
    alert("All results deleted successfully.");
    viewResults(); // Refresh the results
  } else {
    alert("Failed to delete results: " + (res.statusText || "Unknown error"));
  }
}

// ---------------- Auth ----------------
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

// ---------------- Init ----------------
document.addEventListener("DOMContentLoaded", () => {
  const onDashboard = document.getElementById("results") !== null;
  if (onDashboard && !getToken()) {
    window.location.href = "/login";
  }

  if (onDashboard) {
    populateFileDropdown();

    const payload = parseJwt(getToken());
    if (payload?.role !== "admin") {
      const stressCard = document.getElementById("stress-card");
      if (stressCard) stressCard.style.display = "none";
    }

    viewResults(); // first load
  }
});

function parseJwt(token) {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch (e) {
    return null;
  }
}
