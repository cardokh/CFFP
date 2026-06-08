/*
 * Shared table sorter.
 *
 * Responsibilities:
 * - Enable client-side sorting for desktop tables.
 * - Sort currently rendered table rows.
 * - Toggle ascending/descending sort state.
 *
 * Usage:
 * - Add class "shared-table-sort-button" to a button inside a table header.
 * - Add data-sort-column with the zero-based column index.
 * - Optionally add data-sort-type="number" for numeric columns.
 */

function getCellSortValue(row, columnIndex, sortType) {
    const cell =
        row.children[columnIndex];

    const rawValue =
        cell ? cell.textContent.trim() : "";

    if (sortType === "number") {
        const numberValue =
            Number(rawValue.replace(/[^\d.-]/g, ""));

        return Number.isNaN(numberValue)
            ? 0
            : numberValue;
    }

    return rawValue.toLowerCase();
}

function clearTableSortIndicators(table, activeButton) {
    table
        .querySelectorAll(".shared-table-sort-button")
        .forEach((button) => {
            if (button !== activeButton) {
                button.classList.remove("sorted-asc");
                button.classList.remove("sorted-desc");
                button.dataset.sortDirection = "";
            }
        });
}

function sortTableByColumn(table, columnIndex, sortType, direction) {
    const tbody =
        table.querySelector("tbody");

    if (!tbody) {
        return;
    }

    const rows =
        Array.from(tbody.querySelectorAll("tr"));

    rows.sort((firstRow, secondRow) => {
        const firstValue =
            getCellSortValue(
                firstRow,
                columnIndex,
                sortType
            );

        const secondValue =
            getCellSortValue(
                secondRow,
                columnIndex,
                sortType
            );

        if (firstValue < secondValue) {
            return direction === "asc" ? -1 : 1;
        }

        if (firstValue > secondValue) {
            return direction === "asc" ? 1 : -1;
        }

        return 0;
    });

    rows.forEach((row) => {
        tbody.appendChild(row);
    });
}

function handleTableSortClick(event) {
    const button =
        event.currentTarget;

    const table =
        button.closest("table");

    if (!table) {
        return;
    }

    const columnIndex =
        Number(button.dataset.sortColumn);

    if (Number.isNaN(columnIndex)) {
        return;
    }

    const sortType =
        button.dataset.sortType || "text";

    const currentDirection =
        button.dataset.sortDirection;

    const nextDirection =
        currentDirection === "asc"
            ? "desc"
            : "asc";

    clearTableSortIndicators(table, button);

    button.dataset.sortDirection =
        nextDirection;

    button.classList.toggle(
        "sorted-asc",
        nextDirection === "asc"
    );

    button.classList.toggle(
        "sorted-desc",
        nextDirection === "desc"
    );

    sortTableByColumn(
        table,
        columnIndex,
        sortType,
        nextDirection
    );
}

function initializeTableSorting(root = document) {
    root
        .querySelectorAll(".shared-table-sort-button")
        .forEach((button) => {
            button.addEventListener(
                "click",
                handleTableSortClick
            );
        });
}