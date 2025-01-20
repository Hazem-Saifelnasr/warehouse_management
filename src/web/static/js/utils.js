// Float precision
function floatPrecision(number, floatPrecision) {
//    const fieldInner = document.getElementById("formattedNumber").innerText
    fieldInner = number.toFixed(floatPrecision); // Display 123.46
}


function sortTable(tableBodyId, columnIndex) {
    const tableBody = document.getElementById(tableBodyId);
    const rows = Array.from(tableBody.rows);

    // Determine the current sorting order
    const table = tableBody.closest("table"); // Get the parent table
    const isAscending = table.getAttribute("data-sort-order") !== "asc";
    table.setAttribute("data-sort-order", isAscending ? "asc" : "desc");

    // Update sort indicator
    updateSortIndicators(columnIndex, isAscending);
    // Sort rows based on the selected column
    rows.sort((rowA, rowB) => {
        const cellA = rowA.cells[columnIndex].textContent.trim().toLowerCase();
        const cellB = rowB.cells[columnIndex].textContent.trim().toLowerCase();

        if (cellA < cellB) return isAscending ? -1 : 1;
        if (cellA > cellB) return isAscending ? 1 : -1;
        return 0;
    });

    // Append sorted rows back to the table
    rows.forEach(row => tableBody.appendChild(row));
}

function updateSortIndicators(columnIndex, isAscending) {
    const headers = document.querySelectorAll("thead th .sort-indicator");
    headers.forEach((indicator, index) => {
        if (index === columnIndex) {
            indicator.textContent = isAscending ? "▲" : "▼";
        } else {
            indicator.textContent = "";
        }
    });
}

function filterTable(tableBodyId) {
    const input = document.getElementById("searchInput").value.toLowerCase();
    const tableBody = document.getElementById(tableBodyId);
    const rows = Array.from(tableBody.rows);

    rows.forEach(row => {
        const cells = Array.from(row.cells).map(cell => cell.textContent.toLowerCase());
        const matches = cells.some(cellText => cellText.includes(input));
        row.style.display = matches ? "" : "none";
    });
}

// Check if the user has a specific permission
function hasPermission(entity, accessType) {
    return userPermissions.some(
        (perm) =>
            (perm.entity === entity || perm.entity === "*") &&
            (perm.access_type === accessType || perm.access_type === "*")
    );
}

// handles the pages navigation
function changePage(page,size) {
    // Ensure page is greater than 0
    if (page < 1) return;

    // Reload the page with the new page number in query params
    window.location.href = `?page=${page}&size=${size}`;
}

// handles items per page
function changePageSize(size) {
    window.location.href = `?page=1&size=${size}`;
}

//async function callApi(endpoint, options = {}) {
//    try {
//        // Perform the API request
//        const response = await fetch(endpoint, options);
//
//        if (!response.ok) {
//            // Log error if the response status is not OK
//            const errorDetails = await response.json();
//            console.error(`Error: ${response.status} - ${response.statusText}`, errorDetails);
//
//            // Show a user-friendly error message
//            alert(`Error: ${errorDetails.detail || "Unknown error occurred"}`);
//            return null; // Exit early
//        }
//
//        // Parse and return JSON if the response is successful
//        return await response.json();
//    } catch (error) {
//        // Handle network or other unexpected errors
//        console.error("An unexpected error occurred:", error);
//
//        // Show a user-friendly error message
//        alert("Failed to connect to the server. Please try again later.");
//        return null; // Exit early
//    }
//}
//
//// Example usage
//async function fetchReports() {
//    const reports = await callApi("/reports/list");
//    if (reports) {
//        console.log("Reports fetched successfully:", reports);
//        // Process and render reports
//    }
//}
//
//// Call the function to fetch reports
//fetchReports();