/*
 * Shared table search.
 *
 * Responsibilities:
 * - Normalize search input values.
 * - Filter row/data collections using caller-provided searchable text.
 */

function getTableSearchInputValue(searchInputId) {
    const searchInput =
        document.getElementById(searchInputId);

    if (!searchInput) {
        return "";
    }

    return searchInput.value.trim().toLowerCase();
}

function filterTableItems(items, searchTerm, getSearchableText) {
    const normalizedSearchTerm =
        searchTerm.trim().toLowerCase();

    if (!normalizedSearchTerm) {
        return items;
    }

    return items.filter((item) =>
        getSearchableText(item)
            .toLowerCase()
            .includes(normalizedSearchTerm)
    );
}

function enableTableSearchInput(searchInputId) {
    const searchInput =
        document.getElementById(searchInputId);

    if (!searchInput) {
        return;
    }

    searchInput.disabled = false;
}