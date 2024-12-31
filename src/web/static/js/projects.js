document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("addProjectForm");
    if (form) {
        form.onsubmit = async function (event) {
            event.preventDefault();
            const formData = new FormData(this);

            const response = await fetch("/projects/add", {
                method: "POST",
                body: JSON.stringify(Object.fromEntries(formData)),
                headers: { "Content-Type": "application/json" },
            });

            if (response.ok) {
                alert("Project added successfully!");
                window.location.reload();
            } else {
                alert("Error adding project.");
            }
        };
    }
});

function editProject(projectId) {
    // Fetch the user data
    fetch(`/projects/${projectId}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to fetch project data.");
            }
            return response.json();
        })
        .then((project) => {
            // Populate the modal form with project data
            const editProjectModal = new bootstrap.Modal(document.getElementById("editProjectModal"));
            document.getElementById("editProjectId").value = project.id;
            document.getElementById("editProjectName").value = project.project_name;
            document.getElementById("editLocationId").value = project.location_id;

            // Show the modal
            editProjectModal.show();
        })
        .catch((error) => {
            alert("Error loading project data: " + error.message);
        });
}

// Submit the updated user details
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("editProjectForm");
    if (form) {
        form.onsubmit = async function (event) {
            event.preventDefault();
            // Convert form data into a JSON object
            const projectId = document.getElementById("editProjectId").value;

            const formData = new FormData(this); // Gather all form inputs
            formData.delete("id")
            const jsonData = Object.fromEntries(formData); // Convert to a plain object
            jsonData.location_id = parseInt(jsonData.location_id); // Ensure location_id is an integer

            console.log("Request Data:", JSON.stringify(jsonData)); // Debugging

            try {
                const response = await fetch(`/projects/${projectId}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(jsonData), // Convert the object to JSON string
                });
                if (response.ok) {
                    alert("Project updated successfully!");
                    window.location.reload();
                } else {
                    const error = await response.json();
                    console.error("Error Response:", error);
                    alert("Error updating project: " + (error.detail || "Unknown error"));
                }
            } catch (error) {
                console.error("An error occurred:", error);
                alert("Failed to update project.");
            }
        };
    } else {
        console.error("Form element not found!");
    }
});

function deleteProject(projectId) {
    if (confirm("Are you sure you want to delete this project?")) {
        fetch(`/projects/${projectId}`, { method: "DELETE" })
            .then((response) => {
                if (response.ok) {
                    alert("Project deleted successfully!");
                    window.location.reload();
                } else {
                    alert("Error deleting project.");
                }
            });
    }
}
