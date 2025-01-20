function changePage(page) {
    // Ensure page is greater than 0
    if (page < 1) return;

    // Reload the page with the new page number in query params
    window.location.href = `?page=${page}&size={{ size }}`;
}