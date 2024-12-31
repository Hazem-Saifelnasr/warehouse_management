document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("addItemForm");
    if (form) {
        form.onsubmit = async function (event) {
            event.preventDefault();
            // Convert form data into a JSON object
            const formData = new FormData(this); // Gather all form inputs

            try {
                // Step 1: Create the Item without the photo
                const createItemData = {
                    item_code: formData.get("item_code"),
                    description: formData.get("description"),
                    unit_of_measure: formData.get("unit_of_measure"),
                };

                const createItemResponse = await fetch("/items/add", {
                    method: "POST",
                    headers: {"Content-Type": "application/json",},
                    body: JSON.stringify(createItemData), // Send item creation data
                });

                if (!createItemResponse.ok) {
                    const error = await createItemResponse.json();
                    alert("Error creating item: " + (error.detail || "Unknown error"));
                    return;
                }

                const createdItem = await createItemResponse.json();
                const itemId = createdItem.id; // Retrieve the item_id from the response

                // Step 2: Upload the Photo
                const photoFile = formData.get("photo"); // Get the file from the form
                if (photoFile && photoFile.size > 0) {
                    const photoFormData = new FormData();
                    photoFormData.append("file", photoFile);

                    const uploadPhotoResponse = await fetch(`/items/${itemId}/upload-photo`, {
                        method: "POST",
                        body: photoFormData, // Send the file as FormData
                    });

                    if (!uploadPhotoResponse.ok) {
                        const error = await uploadPhotoResponse.json();
                        alert("Error uploading photo: " + (error.detail || "Unknown error"));
                        return;
                    }
                }

                alert("Item added successfully with photo!");
                window.location.reload();

            } catch (error) {
                console.error("An error occurred:", error);
                alert("Failed to add item.");
            }
        };
    } else {
        console.error("Form element not found!");
    }
});

function editItem(itemId) {
    // Fetch the user data
    fetch(`/items/${itemId}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to fetch item data.");
            }
            return response.json();
        })
        .then((item) => {
            // Populate the modal form with user data
            const editItemModal = new bootstrap.Modal(document.getElementById("editItemModal"));
            document.getElementById("editItemId").value = item.id;
            document.getElementById("editItemCode").value = item.item_code;
            document.getElementById("editDescription").value = item.description;
            document.getElementById("editUnitOfMeasure").value = item.unit_of_measure;

            // Show the modal
            editItemModal.show();
        })
        .catch((error) => {
            alert("Error loading item data: " + error.message);
        });
}

// Submit the updated user details
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("editItemForm");
    if (form) {
        form.onsubmit = async function (event) {
            event.preventDefault();
            // Convert form data into a JSON object
            const itemId = document.getElementById("editItemId").value;

            const formData = new FormData(this); // Gather all form inputs
            formData.delete("id")
            const jsonData = Object.fromEntries(formData); // Convert to a plain object
            console.log(jsonData)
            try {
                const response = await fetch(`/items/${itemId}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(jsonData), // Convert the object to JSON string
                });
                console.log("Form Data (as JSON):", JSON.stringify(jsonData));
                if (response.ok) {
                    alert("Item updated successfully!");
                    window.location.reload();
                } else {
                    alert("Error updating item.");
                }
            } catch (error) {
                console.error("An error occurred:", error);
                alert("Failed to update item.");
            }
        };
    } else {
        console.error("Form element not found!");
    }
});


function deleteItem(itemId) {
    if (confirm("Are you sure you want to delete this item?")) {
        fetch(`/items/${itemId}`, { method: "DELETE" })
            .then((response) => {
                if (response.ok) {
                    alert("Item deleted successfully!");
                    window.location.reload();
                } else {
                    alert("Error deleting item.");
                }
            });
    }
}

function uploadPhoto(itemId) {
    const form = document.createElement("form");
    form.setAttribute("method", "POST");
    form.setAttribute("enctype", "multipart/form-data");

    const fileInput = document.createElement("input");
    fileInput.setAttribute("type", "file");
    fileInput.setAttribute("name", "file");
    fileInput.setAttribute("accept", "image/*");
    form.appendChild(fileInput);

    fileInput.addEventListener("change", async function () {
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        try {
            const response = await fetch(`/items/${itemId}/upload-photo`, {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                alert("Photo uploaded successfully!");
                window.location.reload();
            } else {
                const error = await response.json();
                alert("Error uploading photo: " + (error.detail || "Unknown error"));
            }
        } catch (error) {
            console.error("Error uploading photo:", error);
            alert("Failed to upload photo.");
        }
    });

    fileInput.click(); // Trigger the file input dialog
}

function viewPhoto(itemId) {
    fetch(`/items/${itemId}`)
        .then((response) => {
            if (!response.ok) throw new Error("Item not found.");
            return response.json();
        })
        .then((item) => {
            if (item.photo) {
                const photoUrl = `/${item.photo}`; // Construct the full URL
                window.open(photoUrl, "_blank");
            } else {
                alert("No photo available for this item.");
            }
        })
        .catch((error) => {
            console.error("Error fetching item photo:", error);
            alert("Error viewing photo.");
        });
}