document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("addStockForm");
    if (form) {
        form.onsubmit = async function (event) {
            event.preventDefault();
            // Convert form data into a JSON object
            const formData = new FormData(this); // Gather all form inputs
            const jsonData = Object.fromEntries(formData.entries()); // Convert to a plain object

            // Dynamically construct `entity_id` based on entity type and name
            const entityType = jsonData.entity_type;
            const entityName = jsonData.entity_name;
            jsonData.item_id = jsonData.item_code;

            if (entityType === "warehouse") {
                jsonData.warehouse_id = `${entityName}`;
            } else if (entityType === "project") {
                jsonData.project_id = `${entityName}`;
            }

            // Remove `entity_type` and `entity_name` from the JSON object
            delete jsonData.entity_type;
            delete jsonData.entity_name;
            delete jsonData.item_code;

            try {
                const response = await fetch("/stocks/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(jsonData), // Convert the object to JSON string
                });

                if (response.ok) {
                    alert("Stock added successfully!");
                    // window.location.href = "/users"; // Redirect or reload
                    window.location.reload();
                } else {
                    const error = await response.json();
                    alert("Error adding stock: " + (error.detail || "Unknown error"));
                }
            } catch (error) {
                console.error("An error occurred:", error);
                alert("Failed to add stock.");
            }
        };
    } else {
        console.error("Form element not found!");
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("deductStockForm");
    if (form) {
        form.onsubmit = async function (event) {
            event.preventDefault();
            // Convert form data into a JSON object
            const formData = new FormData(this); // Gather all form inputs
            const jsonData = Object.fromEntries(formData.entries()); // Convert to a plain object

            // Dynamically construct `entity_id` based on entity type and name
            const entityType = jsonData.entity_type;
            const entityName = jsonData.entity_name;
            jsonData.item_id = parseInt(jsonData.item_code);

            if (entityType === "warehouse") {
                jsonData.warehouse_id = `${entityName}`;
            } else if (entityType === "project") {
                jsonData.project_id = `${entityName}`;
            }

            // Remove `entity_type` and `entity_name` from the JSON object
            delete jsonData.entity_type;
            delete jsonData.entity_name;
            delete jsonData.item_code;

            try {
                const response = await fetch("/stocks/deduct", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(jsonData), // Convert the object to JSON string
                });
                if (response.ok) {
                    alert("Stock deducted successfully!");
                    // window.location.href = "/users"; // Redirect or reload
                    window.location.reload();
                } else {
                    const error = await response.json();
                    alert("Error deducting stock: " + (error.detail || "Unknown error"));
                }
            } catch (error) {
                console.error("An error occurred:", error);
                alert("Failed to deduct stock.");
            }
        };
    } else {
        console.error("Form element not found!");
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("transferStockForm");
    if (form) {
        form.onsubmit = async function (event) {
            event.preventDefault();
            // Convert form data into a JSON object
            const formData = new FormData(this); // Gather all form inputs
            const jsonData = Object.fromEntries(formData.entries()); // Convert to a plain object

            // Map item_code to item_id
            const item_id = parseInt(jsonData.item_code);

            // Convert `from_entity_type` and `from_entity_name` to appropriate IDs
            let from_id, to_id;
            if (jsonData.from_entity_type === "warehouse") {
                from_id = `from_warehouse_id=${parseInt(jsonData.from_entity_name)}`;
            } else if (jsonData.from_entity_type === "project") {
                from_id = `from_project_id=${parseInt(jsonData.from_entity_name)}`;
            }

            // Convert `to_entity_type` and `to_entity_name` to appropriate IDs
            if (jsonData.to_entity_type === "warehouse") {
                to_id = `to_warehouse_id=${parseInt(jsonData.to_entity_name)}`;
            } else if (jsonData.to_entity_type === "project") {
                to_id = `to_project_id=${parseInt(jsonData.to_entity_name)}`;
            }

            // Construct query parameters
            const queryParams = new URLSearchParams({
                item_id: item_id,
                quantity: jsonData.quantity,
            });

            if (from_id) queryParams.append(...from_id.split("="));
            if (to_id) queryParams.append(...to_id.split("="));

            console.log("Query Parameters:", queryParams.toString());

            try {
                const response = await fetch(`/stocks/transfer?${queryParams.toString()}`, {
                    method: "POST",
                });

                if (response.ok) {
                    alert("Stock transferred successfully!");
                    // window.location.href = "/users"; // Redirect or reload
                    window.location.reload();
                } else {
                    const error = await response.json();
                    alert("Error transferring stock: " + (error.detail || "Unknown error"));
                }
            } catch (error) {
                console.error("An error occurred:", error);
                alert("Failed to transfer stock.");
            }
        };
    } else {
        console.error("Form element not found!");
    }
});


document.addEventListener("DOMContentLoaded", () => {
    // Select all entity type dropdowns
    const entityTypeSelectors = document.querySelectorAll("[id$='EntityType']");
    entityTypeSelectors.forEach(selector => {
        selector.addEventListener("change", (event) => {
            const type = event.target.id.replace("EntityType", "");
            updateEntityList(type); // Update dropdown options
            updateEntityLabel(type); // Update the corresponding label
        });
    });
});

/**
 * Function to fetch the data from tables
 */

let warehouses = [];
let projects = [];

async function fetchData() {
    try {
        const warehouseResponse = await fetch("/warehouses/list");
        const projectResponse = await fetch("/projects/list");

        if (warehouseResponse.ok) {
            warehouses = await warehouseResponse.json();
        } else {
            console.error("Failed to fetch warehouses.");
        }

        if (projectResponse.ok) {
            projects = await projectResponse.json();
        } else {
            console.error("Failed to fetch projects.");
        }
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

/**
 * Function to update the entity list options
 */

async function updateEntityList(type) {
    const entityType = document.getElementById(`${type}EntityType`).value;
    const entityNameSelect = document.getElementById(`${type}EntityName`);

    await fetchData(); // Ensure data is available before populating options


    let options = [];
    if (entityType === "warehouse") {
        options = warehouses.map(w => `<option value="${w.id}">${w.name}</option>`);
    } else if (entityType === "project") {
        options = projects.map(p => `<option value="${p.id}">${p.project_name}</option>`);
    }

    entityNameSelect.innerHTML = options.join("");
}

/**
 * Function to update the label text
 */
function updateEntityLabel(type) {
    const entityType = document.getElementById(`${type}EntityType`).value;
    const entityNameLabel = document.getElementById(`${type}EntityNameLabel`);

    if (!entityNameLabel) {
        console.error(`No label element found with ID '${type}EntityNameLabel'`);
        return;
    }

    if (entityType) {
        entityNameLabel.textContent = `${entityType.charAt(0).toUpperCase() + entityType.slice(1)} Name`;
    }
}