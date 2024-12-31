document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("addLocationForm");
    if (form) {
        form.onsubmit = async function (event) {
            event.preventDefault();
            const formData = new FormData(this);

            const response = await fetch("/locations/add", {
                method: "POST",
                body: JSON.stringify(Object.fromEntries(formData)),
                headers: { "Content-Type": "application/json" },
            });

            if (response.ok) {
                alert("Location added successfully!");
                window.location.reload();
            } else {
                alert("Error adding location.");
            }
        };
    }
});

function editLocation(locationId) {
    // Fetch the user data
    fetch(`/locations/${locationId}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to fetch location data.");
            }
            return response.json();
        })
        .then((location) => {
            // Populate the modal form with user data
            const editLocationModal = new bootstrap.Modal(document.getElementById("editLocationModal"));
            document.getElementById("editLocationId").value = location.id;
            document.getElementById("editLocationName").value = location.name;

            // Show the modal
            editLocationModal.show();
        })
        .catch((error) => {
            alert("Error loading location data: " + error.message);
        });
}

// Submit the updated user details
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("editLocationForm");
    if (form) {
        form.onsubmit = async function (event) {
            event.preventDefault();
            // Convert form data into a JSON object
            const locationId = document.getElementById("editLocationId").value;

            const formData = new FormData(this); // Gather all form inputs
            formData.delete("id")
            const jsonData = Object.fromEntries(formData); // Convert to a plain object
            jsonData.location_id = parseInt(jsonData.location_id);
            console.log(JSON.stringify(jsonData));
            try {
                const response = await fetch(`/locations/${locationId}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(jsonData), // Convert the object to JSON string
                });
                if (response.ok) {
                    alert("Location updated successfully!");
                    window.location.reload();
                } else {
                    alert("Error updating location.");
                }
            } catch (error) {
                console.error("An error occurred:", error);
                alert("Failed to update location.");
            }
        };
    } else {
        console.error("Form element not found!");
    }
});

function deleteLocation(locationId) {
    if (confirm("Are you sure you want to delete this location?")) {
        fetch(`/locations/${locationId}`, { method: "DELETE" })
            .then((response) => {
                if (response.ok) {
                    alert("Location deleted successfully!");
                    window.location.reload();
                } else {
                    alert("Error deleting location.");
                }
            });
    }
}
