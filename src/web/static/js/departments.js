document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("addDepartmentForm");
    if (form) {
        form.onsubmit = async function (event) {
            event.preventDefault();
            // Convert form data into a JSON object
            const formData = new FormData(this); // Gather all form inputs
            const jsonData = Object.fromEntries(formData.entries()); // Convert to a plain object

            try {
                const response = await fetch("/departments/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(jsonData), // Convert the object to JSON string
                });
                if (response.ok) {
                    alert("Department added successfully!");
                    // window.location.href = "/departments"; // Redirect or reload
                    window.location.reload();
                } else {
                    const error = await response.json();
                    alert("Error adding department: " + (error.detail || "Unknown error"));
                }
            } catch (error) {
                console.error("An error occurred:", error);
                alert("Failed to add department.");
            }
        };
    } else {
        console.error("Form element not found!");
    }
});

function editDepartment(departmentId) {
    // Fetch the department data
    fetch(`/departments/${departmentId}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to fetch department data.");
            }
            return response.json();
        })
        .then((department) => {
            // Populate the modal form with department data
            const editDepartmentModal = new bootstrap.Modal(document.getElementById("editDepartmentModal"));
            document.getElementById("editDepartmentId").value = department.id;
            document.getElementById("editName").value = department.name;

            // Show the modal
            editDepartmentModal.show();
        })
        .catch((error) => {
            alert("Error loading department data: " + error.message);
        });
}

// Submit the updated department details
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("editDepartmentForm");
    if (form) {
        form.onsubmit = async function (event) {
            event.preventDefault();
            // Convert form data into a JSON object
            const departmentId = document.getElementById("editDepartmentId").value;

            const formData = new FormData(this); // Gather all form inputs
            formData.delete("id")
            const jsonData = Object.fromEntries(formData); // Convert to a plain object

            console.log("Request Data:", JSON.stringify(jsonData)); // Debugging

            try {
                const response = await fetch(`/departments/${departmentId}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(jsonData), // Convert the object to JSON string
                });
                console.log("Form Data (as JSON):", JSON.stringify(jsonData));
                if (response.ok) {
                    alert("Department updated successfully!");
                    window.location.reload();
                } else {
                    alert("Error updating department.");
                }
            } catch (error) {
                console.error("An error occurred:", error);
                alert("Failed to update department.");
            }
        };
    } else {
        console.error("Form element not found!");
    }
});

function deleteDepartment(departmentId) {
    if (confirm("Are you sure you want to delete this department?")) {
        fetch(`/departments/${departmentId}`, { method: "DELETE" })
            .then((response) => {
                if (response.ok) {
                    alert("Department deleted successfully!");
                    window.location.reload();
                } else {
                    alert("Error deleting department.");
                }
            });
    }
}

function archiveDepartment(departmentId) {
    if (confirm("Are you sure you want to archive this department?")) {
        fetch(`/departments/archive/${departmentId}`, { method: "POST" })
            .then((response) => {
                if (response.ok) {
                    alert("Department archived successfully!");
                    window.location.reload();
                } else {
                    alert("Error archiving department.");
                }
            });
    }
}
