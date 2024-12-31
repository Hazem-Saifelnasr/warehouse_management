document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("addPermissionForm");
    if (form) {
        form.onsubmit = async function (event) {
            event.preventDefault();
            // Convert form data into a JSON object
            const formData = new FormData(this); // Gather all form inputs
            const jsonData = Object.fromEntries(formData.entries()); // Convert to a plain object

            // Transform the properties
            jsonData.user_id = jsonData.user_name;
            jsonData.entity_id = jsonData.entity_name;

            // Delete the unwanted properties
            delete jsonData.user_name;
            delete jsonData.entity_name;

            console.log("Processed JSON Data:", jsonData); // Log the final object

            try {
                const response = await fetch("/permissions/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(jsonData), // Convert the object to JSON string
                });
                if (response.ok) {
                    alert("Permission added successfully!");
                    // window.location.href = "/users"; // Redirect or reload
                    window.location.reload();
                } else {
//                    const error = await response.json();
//                    alert("Error adding permission: " + (error.detail || "Unknown error"));

                    // Log error if the response status is not OK
                    const errorDetails = await response.json();
                    console.error(`Error: ${response.status} - ${response.statusText}`, errorDetails);

                    // Show a user-friendly error message
                    alert(`Error: ${errorDetails.detail || "Unknown error occurred"}`);
                    return null; // Exit early
                }
            } catch (error) {
                console.error("An error occurred:", error);
                alert("Failed to add permission.");
            }
        };
    } else {
        console.error("Form element not found!");
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const entitySelector = document.getElementById("addEntity");
    const entityNameSelector = document.getElementById("addEntityName");

    const entityData = {
        "*": [{ id: "*", name: "All" }],
        item: [],
        project: [],
        warehouse: [],
        location: []
    };

    // Fetch data on page load
    async function fetchEntityData() {
        try {
            const responses = await Promise.all([
                fetch("/items/list"),
                fetch("/projects/list"),
                fetch("/warehouses/list"),
                fetch("/locations/list")
            ]);

            entityData.item = [{ id: "*", item_code: "All" }].concat(responses[0].ok ? await responses[0].json() : []);
            entityData.project = [{ id: "*", project_name: "All" }].concat(responses[1].ok ? await responses[1].json() : []);
            entityData.warehouse = [{ id: "*", name: "All" }].concat(responses[2].ok ? await responses[2].json() : []);
            entityData.location = [{ id: "*", name: "All" }].concat(responses[3].ok ? await responses[3].json() : []);
        } catch (error) {
            console.error("Error fetching entity data:", error);
        }
    }

    fetchEntityData();

    // Update the Entity Name dropdown
    entitySelector.addEventListener("change", () => {
        const selectedEntity = entitySelector.value;
        const options = entityData[selectedEntity]?.map(entity => `<option value="${entity.id}">${entity.name || entity.project_name || entity.item_code || entity.username}</option>`) || [];
        entityNameSelector.innerHTML = options.join("");
    });
});


function deletePermission(permissionId) {
    if (confirm("Are you sure you want to delete this permission?")) {
        fetch(`/permissions/${permissionId}`, { method: "DELETE" })
            .then((response) => {
                if (response.ok) {
                    alert("Permission deleted successfully!");
                    window.location.reload();
                } else {
                    alert("Error deleting permission.");
                }
            });
    }
}
