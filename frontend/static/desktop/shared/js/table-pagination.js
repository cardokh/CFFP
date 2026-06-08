/*
 * Shared table pagination.
 *
 * Responsibilities:
 * - Calculate total pages.
 * - Return paged table items.
 * - Update previous/next button state.
 * - Update pagination status text.
 */

function getTableTotalPages(items, rowsPerPage) {
    return Math.max(
        1,
        Math.ceil(items.length / rowsPerPage)
    );
}

function clampTablePage(currentPage, totalPages) {
    if (currentPage < 1) {
        return 1;
    }

    if (currentPage > totalPages) {
        return totalPages;
    }

    return currentPage;
}

function getPagedTableItems(items, currentPage, rowsPerPage) {
    const startIndex =
        (currentPage - 1) * rowsPerPage;

    const endIndex =
        startIndex + rowsPerPage;

    return items.slice(startIndex, endIndex);
}

function updateTablePaginationControls(config) {
    const totalPages =
        getTableTotalPages(
            config.items,
            config.rowsPerPage
        );

    const currentPage =
        clampTablePage(
            config.currentPage,
            totalPages
        );

    const statusElement =
        document.getElementById(config.statusElementId);

    if (statusElement) {
        statusElement.textContent =
            `Page ${currentPage} of ${totalPages}`;
    }

    setElementDisabled(
        config.previousButtonId,
        currentPage <= 1
    );

    setElementDisabled(
        config.nextButtonId,
        currentPage >= totalPages
    );

    return currentPage;
}