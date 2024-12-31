async function fetchDashboardData() {
    const response = await fetch("/dashboard/metrics", {
    method: 'GET',
    credentials: 'include',
    });
    if (response.ok) {
        const metrics = await response.json();
        document.getElementById("totalItems").innerText = metrics.total_items;
        document.getElementById("totalWarehouses").innerText = metrics.total_warehouses;
        document.getElementById("totalProjects").innerText = metrics.total_projects;
        document.getElementById("totalStock").innerText = metrics.total_stock;

        renderStockDistributionChart(metrics.stock_distribution);
    } else {
        alert("Error fetching dashboard data.");
    }
}

function renderStockDistributionChart(data) {
    const ctx = document.getElementById("stockDistributionChart").getContext("2d");
    new Chart(ctx, {
        type: "pie",
        data: {
            labels: Object.keys(data),
            datasets: [
                {
                    label: "Stock Distribution",
                    data: Object.values(data),
                    backgroundColor: ["#007bff", "#28a745", "#dc3545", "#ffc107"],
                },
            ],
        },
    });
}

// Load dashboard data on page load
document.addEventListener("DOMContentLoaded", fetchDashboardData);
