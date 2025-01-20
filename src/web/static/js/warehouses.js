document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("addWarehouseForm");
    if (form) {
        form.onsubmit = async function (event) {
            event.preventDefault();
            const formData = new FormData(this);
            const jsonData = Object.fromEntries(formData.entries()); // Convert to a plain object

            if (formData.get('capacity') === '') { // Check if budget is an empty string
                jsonData.capacity = null; // Set to null if empty
            }

            const response = await fetch("/warehouses/add", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(jsonData),
            });

            if (response.ok) {
                alert("Warehouse added successfully!");
                window.location.reload();
            } else {
                    const error = await response.json();
                    console.error(`Error: ${response.status} - ${response.statusText}`, error);
                    alert("Error adding warehouse: " + (error.detail || "Unknown error"));
            }
        };
    }
});

function editWarehouse(warehouseId) {
    // Fetch the user data
    fetch(`/warehouses/${warehouseId}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to fetch warehouse data.");
            }
            return response.json();
        })
        .then((warehouse) => {
            // Populate the modal form with warehouse data
            const editWarehouseModal = new bootstrap.Modal(document.getElementById("editWarehouseModal"));
            document.getElementById("editWarehouseId").value = warehouse.id;
            document.getElementById("editName").value = warehouse.name;
            document.getElementById("editCapacity").value = warehouse.capacity;
            document.getElementById("editDescription").value = warehouse.description;
            document.getElementById("editLocationId").value = warehouse.location_id;

            // Show the modal
            editWarehouseModal.show();
        })
        .catch((error) => {
            alert("Error loading warehouse data: " + error.message);
        });
}

// Submit the updated warehouse details
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("editWarehouseForm");
    if (form) {
        form.onsubmit = async function (event) {
            event.preventDefault();
            // Convert form data into a JSON object
            const warehouseId = document.getElementById("editWarehouseId").value;

            const formData = new FormData(this); // Gather all form inputs
            formData.delete("id")
            const jsonData = Object.fromEntries(formData); // Convert to a plain object
            jsonData.location_id = parseInt(jsonData.location_id); // Ensure location_id is an integer
            jsonData.capacity = parseFloat(jsonData.capacity); // Ensure location_id is an integer

            console.log("Request Data:", JSON.stringify(jsonData)); // Debugging

            try {
                const response = await fetch(`/warehouses/${warehouseId}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(jsonData), // Convert the object to JSON string
                });
                if (response.ok) {
                    alert("Warehouse updated successfully!");
                    window.location.reload();
                } else {
                    const error = await response.json();
                    console.error("Error Response:", error);
                    alert("Error updating warehouse: " + (error.detail || "Unknown error"));
                }
            } catch (error) {
                console.error("An error occurred:", error);
                alert("Failed to update warehouse.");
            }
        };
    } else {
        console.error("Form element not found!");
    }
});

function deleteWarehouse(warehouseId) {
    if (confirm("Are you sure you want to delete this warehouse?")) {
        fetch(`/warehouses/${warehouseId}`, { method: "DELETE" })
            .then((response) => {
                if (response.ok) {
                    alert("Warehouse deleted successfully!");
                    window.location.reload();
                } else {
                    alert("Error deleting warehouse.");
                }
            });
    }
}

function archiveWarehouse(warehouseId) {
    if (confirm("Are you sure you want to archive this warehouse?")) {
        fetch(`/warehouses/archive/${warehouseId}`, { method: "POST" })
            .then((response) => {
                if (response.ok) {
                    alert("Warehouse archived successfully!");
                    window.location.reload();
                } else {
                    alert("Error archiving warehouse.");
                }
            });
    }
}
