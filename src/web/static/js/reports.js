document.addEventListener("DOMContentLoaded", function () {
    const reportsTable = document.getElementById("reportsTable");
    if (reportsTable) {
        fetchReports();
    } else {
        console.error("Element with ID 'reportsTable' not found.");
    }
});

async function fetchReports() {
    const reportsTable = document.getElementById("reportsTable");
    if (!reportsTable) {
        console.error("Reports table element not found.");
        return;
    }

    // Display loading indicator
    reportsTable.innerHTML = "<tr><td colspan='3'>Loading...</td></tr>";

    try {
        const response = await fetch("/reports/list");
        if (response.ok) {
            const reports = await response.json();
             reportsTable.innerHTML = reports.map(report => `
                            <tr>
                                <td>${report.name}</td>
                                <td>${new Date(report.generated_at).toLocaleString()}</td>
                                <td>
                                    <button class="btn btn-danger btn-sm" onclick="deleteReport('${ report.file_name }')">Delete</button>
                                    <a href="files/${report.file_name}" class="btn btn-success btn-sm" target="_blank">Download</a>
                                </td>
                            </tr>
                        `).join("");
            } else {
                reportsTable.innerHTML = "<tr><td colspan='3'>No reports found.</td></tr>";
                alert("Error fetching reports.");
            }
    } catch (error) {
        reportsTable.innerHTML = "<tr><td colspan='3'>Error loading reports.</td></tr>";
        console.error("An error occurred:", error);
    }
}


async function generateReport() {
    try {
        const response = await fetch("/reports/generate", { method: "POST" });
        if (response.ok) {
            alert("Report generated successfully!");
            fetchReports();
        } else {
            alert("Error generating report.");
        }
    } catch (error) {
        console.error("An error occurred while generating the report:", error);
        alert("Failed to generate report.");
    }
}

// Load reports on page load
document.addEventListener("DOMContentLoaded", fetchReports);

function deleteReport(fileName) {
    console.log("Attempting to delete report with URL:", fileName);

    if (confirm("Are you sure you want to delete this report?")) {
        const payload = { file_name: fileName }; // Change `fileName` to `file_path` if required by the server.
        console.log("Payload being sent:", payload);

        fetch(`/reports/delete`, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        })
            .then(response => {
                if (response.ok) {
                    alert("Report deleted successfully!");
                    fetchReports();
                } else {
                    return response.json().then(data => {
                        alert("Error deleting report: " + (data.detail || "Unknown error"));
                    });
                }
            })
            .catch(error => {
                console.error("An error occurred:", error);
                alert("Failed to delete report.");
            });
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
document.addEventListener("DOMContentLoaded", () => {
    const reportTypeSelector = document.getElementById("reportType");
    const entityTypeSelector = document.getElementById("entityType");
    const entityIdSelector = document.getElementById("entityId");
    const itemIdSelector = document.getElementById("itemId");

    const entityTypeSelection = document.getElementById("entityTypeSelection");
    const entityIdSelection = document.getElementById("entityIdSelection");
    const itemIdSelection = document.getElementById("itemIdSelection");

    const generateReportButton = document.getElementById("generateReport");

    let locations = [];
    let warehouses = [];
    let projects = [];
    let items = [];

    // Fetch initial data
    async function fetchData() {
        try {
            const locationResponse = await fetch("/locations/list");
            const warehouseResponse = await fetch("/warehouses/list");
            const projectResponse = await fetch("/projects/list");
            const itemResponse = await fetch("/items/list");

            if (locationResponse.ok) locations = await locationResponse.json();
            if (warehouseResponse.ok) warehouses = await warehouseResponse.json();
            if (projectResponse.ok) projects = await projectResponse.json();
            if (itemResponse.ok) items = await itemResponse.json();

            // Populate item list after fetching
            populateItemList();

        } catch (error) {
            console.error("Error fetching data:", error);
        }
    }

    fetchData();

    // Populate item list
    function populateItemList() {
        if (items.length === 0) {
            console.warn("No items available to populate.");
            return;
        }

        itemIdSelector.innerHTML = items
            .map(item => `<option value="${item.id}">${item.item_code}</option>`)
            .join("");
    }

    // Handle report type change
    reportTypeSelector.addEventListener("change", () => {
        const reportType = reportTypeSelector.value;

        // Reset visibility
        entityTypeSelection.style.display = "none";
        entityIdSelection.style.display = "none";
        itemIdSelection.style.display = "none";

        // Adjust visibility based on report type
        if (reportType === "entity_report") {
            populateEntityTypeOptions(["item", "stock", "location", "warehouse", "project"]);
            entityTypeSelection.style.display = "block";
        } else if (reportType === "stock_by_entity_type_report") {
            populateEntityTypeOptions(["location", "warehouse", "project"]);
            entityTypeSelection.style.display = "block";
        } else if (reportType === "stock_by_entity_type_and_id_report") {
            populateEntityTypeOptions(["location", "warehouse", "project"]);
            entityTypeSelection.style.display = "block";
            entityIdSelection.style.display = "block";
        } else if (reportType === "stock_by_item_report") {
            itemIdSelection.style.display = "block";
        }
    });

    // Populate entity type options
    function populateEntityTypeOptions(options) {
        entityTypeSelector.innerHTML = options
            .map(option => `<option value="${option}">${option.charAt(0).toUpperCase() + option.slice(1)}</option>`)
            .join("");
    }

    // Handle entity type change
    entityTypeSelector.addEventListener("change", () => {
        const reportType = reportTypeSelector.value;
        const entityType = entityTypeSelector.value;

        // Populate entity list based on the selected type
        let options = [];
        if (entityType === "warehouse" & (reportType !== "entity_report" &  reportType !== "stock_by_entity_type_report")){
            options = warehouses.map(w => `<option value="${w.id}">${w.name}</option>`);
        } else if (entityType === "project" & (reportType !== "entity_report" &  reportType !== "stock_by_entity_type_report")) {
            options = projects.map(p => `<option value="${p.id}">${p.project_name}</option>`);
        } else if (entityType === "location" & (reportType !== "entity_report" &  reportType !== "stock_by_entity_type_report")) {
            options = locations.map(l => `<option value="${l.id}">${l.name}</option>`);
        } else if (entityType === "item" & (reportType !== "entity_report" &  reportType !== "stock_by_entity_type_report")) {
            options = items.map(i => `<option value="${i.id}">${i.item_code}</option>`);
        }

        entityIdSelector.innerHTML = options.join("");
        entityIdSelection.style.display = options.length > 0 ? "block" : "none";
    });

//    // Generate report
//    exportReportButton.addEventListener("click", () => {
//        const reportType = reportTypeSelector.value;
//        const entityType = entityTypeSelector.value;
//        const entityId = entityIdSelector.value;
//        const itemId = itemIdSelector.value;
//
//        let url = "";
//        if (reportType === "entity_report") {
//            url = `/reports/${entityType}`;
//        } else if (reportType === "stock_by_entity_type_report") {
//            url = `/reports/stock/${entityType}`;
//        } else if (reportType === "stock_by_entity_type_and_id_report") {
//            url = `/reports/stock/${entityType}/${entityId}`;
//        } else if (reportType === "stock_by_item_report") {
//            url = `/reports/stock/item/${itemId}`;
//        }
//
//        if (url) {
//            fetch(url, {method: "GET",});
////            window.open(url, "_blank");
//            window.location.reload();
//        } else {
//            alert("Invalid report selection!");
//        }
//    });
});

document.addEventListener("DOMContentLoaded", () => {
    const dynamicReportTable = document.getElementById("dynamicReportTable");
    const dynamicReportTableHeader = document.getElementById("dynamicReportTableHeader");
    const dynamicReportTableBody = document.getElementById("dynamicReportTableBody");

    // Function to fetch and populate the dynamic table
    async function fetchAndPopulateReportData(url) {
        try {
            const response = await fetch(url);
            if (response.ok) {
                const result = await response.json();
                const data = result["data"]
                console.log(data)
                if (data.length > 0) {
                    // Generate table headers from object keys
                    const headers = Object.keys(data[0]);
                    console.log(headers)
                    dynamicReportTableHeader.innerHTML = `
                        <tr>
                            ${headers.map(header => `<th>${header.charAt(0).toUpperCase() + header.slice(1)}</th>`).join("")}
                        </tr>
                    `;

                    // Generate table rows
                    dynamicReportTableBody.innerHTML = data.map(row => `
                        <tr>
                            ${headers.map(header => `<td>${row[header]}</td>`).join("")}
                        </tr>
                    `).join("");

                    // Show the table
                    dynamicReportTable.style.display = "table";
                } else {
                    alert("No data available for this report.");
                    dynamicReportTable.style.display = "none";
                }
            } else {
                alert("Failed to fetch report data.");
            }
        } catch (error) {
            console.error("Error fetching report data:", error);
            alert("An error occurred while fetching the report data.");
        }
    }

    // Event listener for generating report
    const viewReportButton = document.getElementById("viewReport");
    viewReportButton.addEventListener("click", () => {
        const reportType = document.getElementById("reportType").value;
        const entityType = document.getElementById("entityType")?.value;
        const entityId = document.getElementById("entityId")?.value;
        const itemId = document.getElementById("itemId")?.value;

        let url = "";
        if (reportType === "entity_report") {
            url = `/reports/${entityType}`;
        } else if (reportType === "stock_by_entity_type_report") {
            url = `/reports/stock/${entityType}`;
        } else if (reportType === "stock_by_entity_type_and_id_report") {
            url = `/reports/stock/${entityType}/${entityId}`;
        } else if (reportType === "stock_by_item_report") {
            url = `/reports/stock/item/${itemId}`;
        }

        if (url) {
            fetchAndPopulateReportData(url); // Fetch and populate table

        } else {
            alert("Invalid report selection!");
        }
    });
});
