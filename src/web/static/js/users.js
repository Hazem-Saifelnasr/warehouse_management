document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("addUserForm");
    if (form) {
        form.onsubmit = async function (event) {
            event.preventDefault();
            // Convert form data into a JSON object
            const formData = new FormData(this); // Gather all form inputs
            const jsonData = Object.fromEntries(formData.entries()); // Convert to a plain object

            try {
                const response = await fetch("/users/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(jsonData), // Convert the object to JSON string
                });
                if (response.ok) {
                    alert("User added successfully!");
                    // window.location.href = "/users"; // Redirect or reload
                    window.location.reload();
                } else {
                    const error = await response.json();
                    alert("Error adding user: " + (error.detail || "Unknown error"));
                }
            } catch (error) {
                console.error("An error occurred:", error);
                alert("Failed to add user.");
            }
        };
    } else {
        console.error("Form element not found!");
    }
});

function editUser(userId) {
    // Fetch the user data
    fetch(`/users/${userId}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to fetch user data.");
            }
            return response.json();
        })
        .then((user) => {
            // Populate the modal form with user data
            const editUserModal = new bootstrap.Modal(document.getElementById("editUserModal"));
            document.getElementById("editUserId").value = user.id;
            document.getElementById("editEmployeeId").value = user.employee_id;
            document.getElementById("editUsername").value = user.username;
            document.getElementById("editEmail").value = user.email;
            document.getElementById("editRole").value = user.role;

            // Show the modal
            editUserModal.show();
        })
        .catch((error) => {
            alert("Error loading user data: " + error.message);
        });
}

// Submit the updated user details
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("editUserForm");
    if (form) {
        form.onsubmit = async function (event) {
            event.preventDefault();
            // Convert form data into a JSON object
            const userId = document.getElementById("editUserId").value;

            const formData = new FormData(this); // Gather all form inputs
            formData.delete("id")
            const jsonData = Object.fromEntries(formData); // Convert to a plain object

            try {
                const response = await fetch(`/users/${userId}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(jsonData), // Convert the object to JSON string
                });
                console.log("Form Data (as JSON):", JSON.stringify(jsonData));
                if (response.ok) {
                    alert("User updated successfully!");
                    window.location.reload();
                } else {
                    alert("Error updating user.");
                }
            } catch (error) {
                console.error("An error occurred:", error);
                alert("Failed to update user.");
            }
        };
    } else {
        console.error("Form element not found!");
    }
});

function deleteUser(userId) {
    if (confirm("Are you sure you want to delete this user?")) {
        fetch(`/users/${userId}`, { method: "DELETE" })
            .then((response) => {
                if (response.ok) {
                    alert("User deleted successfully!");
                    window.location.reload();
                } else {
                    alert("Error deleting user.");
                }
            });
    }
}
