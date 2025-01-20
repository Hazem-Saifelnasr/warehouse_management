async function restoreEntity(entityType, entityId) {
    const response = await fetch(`/${entityType}s/restore/${entityId}`, { method: 'POST' });
    if (response.ok) {
        alert(`${entityType} restored successfully.`);
        location.reload();
    } else {
        alert(`Failed to restore ${entityType}.`);
    }
}

async function deleteEntity(entityType, entityId) {
    const confirmation = confirm(`Are you sure you want to permanently delete this ${entityType}?`);
    if (!confirmation) {
        return; // Exit if the user cancels
    }

    try {
        // Show a loading spinner or disable buttons (optional)
        const response = await fetch(`/${entityType}s/permanent/${entityId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            alert(`${entityType} deleted successfully.`);
            location.reload(); // Reload the page to refresh the table or UI
        } else {
            const errorData = await response.json(); // Parse JSON error message from the server
            alert(`Failed to delete ${entityType}: ${errorData.detail || 'Unknown error.'}`);
        }
    } catch (error) {
        // Handle network or other unexpected errors
        console.error('Error deleting entity:', error);
        alert(`An error occurred while deleting the ${entityType}. Please try again later.`);
    } finally {
        // Hide loading spinner or re-enable buttons (optional)
    }
}