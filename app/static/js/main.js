// ---------------- Utils ----------------
function showSpinner() {
  document.getElementById("spinner").style.display = "flex";
}
function hideSpinner() {
  document.getElementById("spinner").style.display = "none";
}
function getToken() {
  return localStorage.getItem("token");
}
function parseJwt(token) {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch {
    return null;
  }
}
function isAdmin() {
  const payload = parseJwt(getToken());
  return payload?.role === "admin";
}

// ---------------- Upload ----------------
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
    await viewUploads();
  } finally {
    hideSpinner();
  }
}

async function populateFileDropdown(page = 1, limit = 50, sort = "filename", order = "asc", filter = "") {
  const stressSelect = document.getElementById("stress-file");

  try {
    let url = `/upload/list?page=${page}&limit=${limit}&sort=${sort}&order=${order}`;
    if (filter) url += `&q=${encodeURIComponent(filter)}`;

    const res = await fetch(url, {
      headers: { "Authorization": "Bearer " + getToken() }
    });
    const data = await res.json();

    if (stressSelect) {
      stressSelect.innerHTML = "";

      if (!data.results || data.results.length === 0) {
        const option = new Option("No files available", "", true, true);
        option.disabled = true;
        stressSelect.appendChild(option);
        return;
      }

      data.results.forEach(file => {
        const resolutionText = file.resolution ? ` (${file.resolution})` : "";
        stressSelect.appendChild(new Option(`${file.filename}${resolutionText}`, file.filename));
      });
    }
  } catch (err) {
    console.error("Failed to load files:", err);
  }
}

async function deleteUpload(filename) {
  if (!confirm(`Delete upload "${filename}"?`)) return;

  showSpinner();
  const res = await fetch(`/upload/${filename}`, {
    method: "DELETE",
    headers: { "Authorization": "Bearer " + getToken() }
  });
  hideSpinner();

  if (res.ok) {
    alert(`Upload "${filename}" deleted`);
    viewUploads();
    populateFileDropdown();
  } else {
    const data = await res.json();
    alert("Error: " + (data.error || "Failed to delete"));
  }
}

// ---------------- Processing ----------------
async function processUpload(filename) {
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
  await viewResults(currentPage, sortColumn, sortDirection, currentFilter);
}

// ---------------- Results ----------------
let currentPage = 1;
const resultsPerPage = 5;
let sortColumn = "timestamp";
let sortDirection = "desc";
let totalPages = 1;
let currentFilter = "";

async function viewResults(page = 1, sort = sortColumn, order = sortDirection, filter = currentFilter) {
  showSpinner();
  let url = `/results/metadata?page=${page}&limit=${resultsPerPage}&sort=${sort}&order=${order}`;
  if (filter) url += `&input=${encodeURIComponent(filter)}`;

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
          <th>Actions</th>
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
        <td>
          ${isAdmin() ? `<button class="danger-btn" onclick="deleteResult('${r.output}')">Delete</button>` : ""}
        </td>
      </tr>
    `;
  });

  html += "</tbody></table>";
  resultsDiv.innerHTML = html;

  renderPagination(paginationDiv, totalPages, viewResults);
}

async function deleteResult(filename) {
  if (!confirm(`Delete result "${filename}"?`)) return;

  showSpinner();
  const res = await fetch(`/results/${filename}`, {
    method: "DELETE",
    headers: { "Authorization": "Bearer " + getToken() }
  });
  hideSpinner();

  if (res.ok) {
    alert(`Result "${filename}" deleted`);
    viewResults(currentPage, sortColumn, sortDirection, currentFilter);
  } else {
    const data = await res.json();
    alert("Error: " + (data.error || "Failed to delete"));
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
  currentFilter = document.getElementById("filter-input").value.trim();
  viewResults(1, sortColumn, sortDirection, currentFilter);
}

async function clearData() {
  if (!confirm("Are you sure you want to delete all results? This action cannot be undone.")) return;

  const res = await fetch("/results/clear", {
    method: "DELETE",
    headers: { "Authorization": "Bearer " + getToken() }
  });

  if (res.ok) {
    alert("All results deleted successfully.");
    viewResults();
  } else {
    alert("Failed to delete results: " + (res.statusText || "Unknown error"));
  }
}

// ---------------- Uploads table ----------------
let currentUploadsPage = 1;
const uploadsPerPage = 5;
let uploadsSortColumn = "filename";
let uploadsSortDirection = "asc";
let uploadsFilter = "";

async function viewUploads(page = 1, sort = uploadsSortColumn, order = uploadsSortDirection, q = uploadsFilter) {
  showSpinner();
  let url = `/upload/list?page=${page}&limit=${uploadsPerPage}&sort=${sort}&order=${order}`;
  if (q) url += `&q=${encodeURIComponent(q)}`;

  const res = await fetch(url, {
    headers: { "Authorization": "Bearer " + getToken() }
  });
  const data = await res.json();
  hideSpinner();

  currentUploadsPage = data.page;
  renderUploadsPage(data.results, data.total);
}

function renderUploadsPage(files, total) {
  const uploadsDiv = document.getElementById("uploads-list");
  const paginationDiv = document.getElementById("uploads-pagination");

  let html = `
    <table class="results-table">
      <thead>
        <tr>
          <th onclick="changeUploadsSort('filename')">Filename${getUploadsSortIndicator("filename")}</th>
          <th>Thumbnail</th>
          <th onclick="changeUploadsSort('resolution')">Resolution${getUploadsSortIndicator("resolution")}</th>
          <th onclick="changeUploadsSort('size')">Size (KB)${getUploadsSortIndicator("size")}</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
  `;

  files.forEach(f => {
    html += `
      <tr>
        <td>${f.filename}</td>
        <td>
          <a href="/upload/${f.filename}" target="_blank">
            <img src="/upload/${f.filename}" alt="Uploaded" class="thumbnail">
          </a>
        </td>
        <td>${f.resolution}</td>
        <td>${(f.size_bytes / 1024).toFixed(1)}</td>
        <td>
          <button onclick="processUpload('${f.filename}')">Process</button>
          ${isAdmin() ? `<button class="danger-btn" onclick="deleteUpload('${f.filename}')">Delete</button>` : ""}
        </td>
      </tr>
    `;
  });

  html += "</tbody></table>";
  uploadsDiv.innerHTML = html;

  renderPagination(paginationDiv, Math.ceil(total / uploadsPerPage), viewUploads);
}

function changeUploadsSort(column) {
  if (uploadsSortColumn === column) {
    uploadsSortDirection = uploadsSortDirection === "asc" ? "desc" : "asc";
  } else {
    uploadsSortColumn = column;
    uploadsSortDirection = "asc";
  }
  viewUploads(1, uploadsSortColumn, uploadsSortDirection, uploadsFilter);
}

function getUploadsSortIndicator(column) {
  if (uploadsSortColumn === column) {
    return uploadsSortDirection === "asc" ? " ▲" : " ▼";
  }
  return " ⇅";
}

function applyUploadsFilter() {
  uploadsFilter = document.getElementById("uploads-filter-input").value.trim();
  viewUploads(1, uploadsSortColumn, uploadsSortDirection, uploadsFilter);
}

// ---------------- Pagination helper ----------------
function renderPagination(container, totalPages, callback) {
  container.innerHTML = "";
  if (totalPages <= 1) return;

  const prevBtn = document.createElement("button");
  prevBtn.textContent = "Prev";
  prevBtn.disabled = currentPage === 1;
  prevBtn.onclick = () => callback(currentPage - 1);
  container.appendChild(prevBtn);

  for (let i = 1; i <= totalPages; i++) {
    const btn = document.createElement("button");
    btn.textContent = i;
    if (i === currentPage) btn.classList.add("active");
    btn.onclick = () => callback(i);
    container.appendChild(btn);
  }

  const nextBtn = document.createElement("button");
  nextBtn.textContent = "Next";
  nextBtn.disabled = currentPage === totalPages;
  nextBtn.onclick = () => callback(currentPage + 1);
  container.appendChild(nextBtn);
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
    return;
  }

  if (onDashboard) {
    populateFileDropdown();

    if (!isAdmin()) {
      const stressCard = document.getElementById("stress-card");
      if (stressCard) stressCard.style.display = "none";

      const clearBtn = document.getElementById("clear-data-btn");
      if (clearBtn) clearBtn.style.display = "none";
    }

    viewResults();
    viewUploads();
  }
});