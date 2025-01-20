function handlePendingApproval(approvalId, action) {
    fetch(`/pending_approvals/${approvalId}/${action}`, {
        method: "POST",
    })
        .then(response => {
            if (response.ok) {
                alert(`Request ${action}d successfully!`);
                fetchPendingApprovals(); // Refresh the list
            } else {
                response.json().then(data => {
                    alert(`Error: ${data.detail}`);
                });
            }
        })
        .catch(error => console.error(`Error ${action}ing request:`, error));
}