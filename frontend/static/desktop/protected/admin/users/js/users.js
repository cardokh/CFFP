const USERS_MESSAGE_ID = "usersMessage";
const USERS_TABLE_BODY_ID = "usersTableBody";
const USERS_SEARCH_INPUT_ID = "usersSearchInput";

const USERS_PREVIOUS_PAGE_BUTTON_ID =
    "usersPreviousPageButton";

const USERS_PAGINATION_STATUS_ID =
    "usersPaginationStatus";

const USERS_NEXT_PAGE_BUTTON_ID =
    "usersNextPageButton";

const ADMIN_TABLE_ROWS_PER_PAGE_STORAGE_KEY =
    "adminTableRowsPerPage";

const DEFAULT_ADMIN_TABLE_ROWS_PER_PAGE =
    10;

const ALLOWED_ADMIN_TABLE_ROWS_PER_PAGE_VALUES =
    [10, 25, 50];

let allUsers =
    [];

let currentUsersPage =
    1;


function navigateToEditUser(userId) {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.users.edit(userId);
}


function navigateToCreateUser() {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.users.create;
}


function navigateToAdminDashboard() {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.dashboard;
}


function handleUserRowClick(event) {
    const row =
        event.target.closest("tr[data-user-id]");

    if (!row) {
        return;
    }

    const userId =
        row.dataset.userId;

    if (!userId) {
        showErrorMessage(
            USERS_MESSAGE_ID,
            "User ID is missing."
        );

        return;
    }

    navigateToEditUser(userId);
}


function formatBoolean(value) {
    return value ? "Yes" : "No";
}


function getAdminTableRowsPerPage() {
    const savedRowsPerPage =
        Number(
            localStorage.getItem(
                ADMIN_TABLE_ROWS_PER_PAGE_STORAGE_KEY
            )
        );

    if (
        ALLOWED_ADMIN_TABLE_ROWS_PER_PAGE_VALUES.includes(
            savedRowsPerPage
        )
    ) {
        return savedRowsPerPage;
    }

    return DEFAULT_ADMIN_TABLE_ROWS_PER_PAGE;
}


function getSearchInputValue() {
    return getTableSearchInputValue(
        USERS_SEARCH_INPUT_ID
    );
}


function getSearchableUserText(user) {
    return [
        user.userId,
        user.displayName,
        user.email,
        formatBoolean(user.isActive),
        formatBoolean(user.isVerified),
        formatBoolean(user.isAdmin)
    ]
        .join(" ")
        .toLowerCase();
}


function filterUsers(searchTerm) {
    return filterTableItems(
        allUsers,
        searchTerm,
        getSearchableUserText
    );
}


function getTotalUserPages(users) {
    return getTableTotalPages(
        users,
        getAdminTableRowsPerPage()
    );
}


function getPagedUsers(users) {
    return getPagedTableItems(
        users,
        currentUsersPage,
        getAdminTableRowsPerPage()
    );
}


function updateUsersPaginationControls(filteredUsers) {
    currentUsersPage =
        updateTablePaginationControls({
            items: filteredUsers,
            currentPage: currentUsersPage,
            rowsPerPage: getAdminTableRowsPerPage(),
            previousButtonId:
                USERS_PREVIOUS_PAGE_BUTTON_ID,
            nextButtonId:
                USERS_NEXT_PAGE_BUTTON_ID,
            statusElementId:
                USERS_PAGINATION_STATUS_ID
        });
}


function renderUsersTable(users) {
    const tableBody =
        document.getElementById(USERS_TABLE_BODY_ID);

    tableBody.innerHTML =
        users.map((user) => `
            <tr data-user-id="${escapeHtml(user.userId)}">
                <td>${escapeHtml(user.userId)}</td>

                <td>
                    ${escapeHtml(user.displayName)}
                </td>

                <td>
                    ${escapeHtml(user.email)}
                </td>

                <td>
                    ${formatBoolean(user.isActive)}
                </td>

                <td>
                    ${formatBoolean(user.isVerified)}
                </td>

                <td>
                    ${formatBoolean(user.isAdmin)}
                </td>
            </tr>
        `).join("");

    initializeTableSorting();
}


function renderTableMessage(message) {
    const tableBody =
        document.getElementById(USERS_TABLE_BODY_ID);

    tableBody.innerHTML = `
        <tr>
            <td colspan="6">
                ${escapeHtml(message)}
            </td>
        </tr>
    `;
}


function renderEmptyUsersState() {
    renderTableMessage("No users found.");
}


function renderEmptySearchState() {
    renderTableMessage("No matching users found.");
}


function renderUsersLoadError() {
    renderTableMessage("Failed to load users.");
}


function renderUsersForCurrentState() {
    const filteredUsers =
        filterUsers(getSearchInputValue());

    if (filteredUsers.length === 0) {
        renderEmptySearchState();

        updateUsersPaginationControls(filteredUsers);

        return;
    }

    updateUsersPaginationControls(filteredUsers);

    const pagedUsers =
        getPagedUsers(filteredUsers);

    renderUsersTable(pagedUsers);
}


function handleSearchInput() {
    hideMessage(USERS_MESSAGE_ID);

    currentUsersPage =
        1;

    renderUsersForCurrentState();
}


function handlePreviousPageClick() {
    if (currentUsersPage <= 1) {
        return;
    }

    currentUsersPage -=
        1;

    renderUsersForCurrentState();
}


function handleNextPageClick() {
    const filteredUsers =
        filterUsers(getSearchInputValue());

    const totalPages =
        getTotalUserPages(filteredUsers);

    if (currentUsersPage >= totalPages) {
        return;
    }

    currentUsersPage +=
        1;

    renderUsersForCurrentState();
}


function enableUsersSearch() {
    enableTableSearchInput(
        USERS_SEARCH_INPUT_ID
    );
}


async function loadUsers() {
    hideMessage(USERS_MESSAGE_ID);

    try {
        const data =
            await getJson(
                LLA_API_ENDPOINTS.admin.users.list
            );

        const users =
            data.users;

        if (!users || users.length === 0) {
            allUsers = [];

            renderEmptyUsersState();

            updateUsersPaginationControls(allUsers);

            return;
        }

        allUsers =
            users;

        currentUsersPage =
            1;

        renderUsersForCurrentState();

        enableUsersSearch();

    } catch (error) {
        console.error(error);

        renderUsersLoadError();

        showErrorMessage(
            USERS_MESSAGE_ID,
            error.message || "Failed to load users."
        );
    }
}


document
    .getElementById(USERS_TABLE_BODY_ID)
    .addEventListener(
        "click",
        handleUserRowClick
    );

document
    .getElementById("backToAdminButton")
    .addEventListener(
        "click",
        navigateToAdminDashboard
    );

document
    .getElementById("addUserButton")
    .addEventListener(
        "click",
        navigateToCreateUser
    );

document
    .getElementById(USERS_SEARCH_INPUT_ID)
    .addEventListener(
        "input",
        handleSearchInput
    );

document
    .getElementById(USERS_PREVIOUS_PAGE_BUTTON_ID)
    .addEventListener(
        "click",
        handlePreviousPageClick
    );

document
    .getElementById(USERS_NEXT_PAGE_BUTTON_ID)
    .addEventListener(
        "click",
        handleNextPageClick
    );

loadUsers();