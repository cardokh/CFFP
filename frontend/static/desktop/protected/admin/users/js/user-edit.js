let originalUserData = null;
let originalAssignedLessonIds = [];

let assignedLessons = [];
let availableLessons = [];

let currentUserIsProtectedAdmin =
    false;

let leaveWithoutSavingConfirmed =
    false;

const USER_EDIT_FORM_ID = "userEditForm";
const USER_EDIT_MESSAGE_ID = "userEditMessage";

const ADD_USER_BUTTON_ID = "addUserButton";
const DELETE_USER_BUTTON_ID = "deleteUserButton";
const SAVE_USER_BUTTON_ID = "saveUserButton";

const AVAILABLE_LESSON_SELECT_ID =
    "availableLessonSelect";

const ASSIGNED_LESSONS_TABLE_BODY_ID =
    "assignedLessonsTableBody";


function getUserIdFromUrl() {
    const params =
        new URLSearchParams(window.location.search);

    return params.get("userId");
}


function navigateBackToUsers() {
    const hasChanges =
        hasUserChanged(getFormData());

    if (!hasChanges) {
        window.location.href =
            LLA_PATHS.desktop.protected.admin.users.list;

        return;
    }

    if (!leaveWithoutSavingConfirmed) {
        leaveWithoutSavingConfirmed =
            true;

        showInfoMessage(
            USER_EDIT_MESSAGE_ID,
            "Unsaved changes detected. Click Save to apply your changes or click Back again to leave without saving."
        );

        return;
    }

    window.location.href =
        LLA_PATHS.desktop.protected.admin.users.list;
}


function resetLeaveWithoutSavingConfirmation() {
    leaveWithoutSavingConfirmed =
        false;
}


function navigateToUserCreate() {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.users.create;
}


function isProtectedAdminUser(user) {
    return Number(user.userId) === 1 || user.isAdmin === true;
}


function setProtectedAdminUserState(user) {
    currentUserIsProtectedAdmin =
        isProtectedAdminUser(user);

    if (!currentUserIsProtectedAdmin) {
        return;
    }

    setFormDisabled(USER_EDIT_FORM_ID, true);
    setElementDisabled(AVAILABLE_LESSON_SELECT_ID, true);
    setElementDisabled("addLessonButton", true);
    setElementDisabled(DELETE_USER_BUTTON_ID, true);
    setElementDisabled(SAVE_USER_BUTTON_ID, true);

    showInfoMessage(
        USER_EDIT_MESSAGE_ID,
        "Admin users cannot be edited or deleted."
    );
}


async function deleteUser(userId) {
    if (currentUserIsProtectedAdmin || Number(userId) === 1) {
        showInfoMessage(
            USER_EDIT_MESSAGE_ID,
            "Admin users cannot be deleted."
        );

        return;
    }

    const confirmed =
        confirm("Are you sure you want to delete this user?");

    if (!confirmed) {
        return;
    }

    hideMessage(USER_EDIT_MESSAGE_ID);

    setElementDisabled(DELETE_USER_BUTTON_ID, true);
    setButtonText(DELETE_USER_BUTTON_ID, "Deleting...");

    try {
        const data =
            await deleteJson(
                LLA_API_ENDPOINTS.admin.users.byId(userId)
            );

        if (!data.success) {
            throw new Error(
                data.error || "Failed to delete user."
            );
        }

        window.location.href =
            LLA_PATHS.desktop.protected.admin.users.list;

    } catch (error) {
        showErrorMessage(
            USER_EDIT_MESSAGE_ID,
            error.message || "Failed to delete user."
        );

        setElementDisabled(DELETE_USER_BUTTON_ID, false);
        setButtonText(DELETE_USER_BUTTON_ID, "Delete User");
    }
}


function fillEditForm(user) {
    document.getElementById("userId").value =
        user.userId;

    document.getElementById("displayName").value =
        user.displayName;

    document.getElementById("email").value =
        user.email;

    document.getElementById("isActive").checked =
        Boolean(user.isActive);

    document.getElementById("isVerified").checked =
        Boolean(user.isVerified);

    originalUserData = {
        displayName: user.displayName,
        email: user.email,
        isActive: Boolean(user.isActive),
        isVerified: Boolean(user.isVerified)
    };

    setProtectedAdminUserState(user);
}


function getFormData() {
    return {
        displayName:
            document.getElementById("displayName").value.trim(),

        email:
            document.getElementById("email").value.trim(),

        isActive:
            document.getElementById("isActive").checked,

        isVerified:
            document.getElementById("isVerified").checked
    };
}


function getAssignedLessonIds() {
    return assignedLessons.map(
        (lesson) => Number(lesson.lessonId)
    );
}


function haveAssignedLessonsChanged() {
    const current =
        [...getAssignedLessonIds()].sort();

    const original =
        [...originalAssignedLessonIds].sort();

    return JSON.stringify(current) !== JSON.stringify(original);
}


function hasUserChanged(currentUserData) {
    if (!originalUserData) {
        return false;
    }

    const userChanged =
        currentUserData.displayName !== originalUserData.displayName ||
        currentUserData.email !== originalUserData.email ||
        currentUserData.isActive !== originalUserData.isActive ||
        currentUserData.isVerified !== originalUserData.isVerified;

    return userChanged || haveAssignedLessonsChanged();
}


function normalizeAvailableLesson(lesson) {
    return {
        lessonId: lesson.lessonId,
        lessonTitle: lesson.title || lesson.lessonTitle,
        categoryName: lesson.categoryName,
        lessonTypeName: lesson.lessonTypeName,
        statusName:
            lesson.statusName ||
            lesson.status ||
            lesson.lessonStatusName ||
            "Not started"
    };
}


function formatLessonStatus(lesson) {
    return (
        lesson.statusName ||
        lesson.status ||
        lesson.lessonStatusName ||
        "Not started"
    );
}


function renderAvailableLessonsDropdown() {
    const select =
        document.getElementById(
            AVAILABLE_LESSON_SELECT_ID
        );

    const assignedLessonIds =
        getAssignedLessonIds();

    const selectableLessons =
        availableLessons.filter((lesson) =>
            !assignedLessonIds.includes(
                Number(lesson.lessonId)
            )
        );

    select.innerHTML =
        `<option value="">Select lesson</option>`;

    selectableLessons.forEach((lesson) => {
        const option =
            document.createElement("option");

        option.value =
            lesson.lessonId;

        option.textContent =
            lesson.title || lesson.lessonTitle;

        select.appendChild(option);
    });

    const disabled =
        currentUserIsProtectedAdmin ||
        selectableLessons.length === 0;

    setElementDisabled(
        AVAILABLE_LESSON_SELECT_ID,
        disabled
    );

    setElementDisabled(
        "addLessonButton",
        disabled
    );
}


function removeAssignedLesson(lessonId) {
    if (currentUserIsProtectedAdmin) {
        showInfoMessage(
            USER_EDIT_MESSAGE_ID,
            "Admin users cannot be edited."
        );

        return;
    }

    assignedLessons =
        assignedLessons.filter(
            (lesson) =>
                Number(lesson.lessonId) !== Number(lessonId)
        );

    resetLeaveWithoutSavingConfirmation();
    renderAssignedLessonsTable();
    renderAvailableLessonsDropdown();
}


function renderAssignedLessonsTable() {
    const tableBody =
        document.getElementById(
            ASSIGNED_LESSONS_TABLE_BODY_ID
        );

    if (assignedLessons.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5">
                    No lessons assigned.
                </td>
            </tr>
        `;

        return;
    }

    tableBody.innerHTML =
        assignedLessons.map((lesson) => `
            <tr>
                <td>
                    ${escapeHtml(lesson.lessonTitle || "")}
                </td>

                <td>
                    ${escapeHtml(lesson.categoryName || "")}
                </td>

                <td>
                    ${escapeHtml(lesson.lessonTypeName || "")}
                </td>

                <td>
                    ${escapeHtml(formatLessonStatus(lesson))}
                </td>

                <td>
                    <button
                        class="user-table-action-button remove-action-button"
                        type="button"
                        onclick="removeAssignedLesson(${lesson.lessonId})"
                        aria-label="Remove lesson"
                        title="Remove lesson"
                        ${currentUserIsProtectedAdmin ? "disabled" : ""}>
                        🗑
                    </button>
                </td>
            </tr>
        `).join("");
}


function addSelectedLesson() {
    if (currentUserIsProtectedAdmin) {
        showInfoMessage(
            USER_EDIT_MESSAGE_ID,
            "Admin users cannot be edited."
        );

        return;
    }

    const select =
        document.getElementById(
            AVAILABLE_LESSON_SELECT_ID
        );

    const lessonId =
        Number(select.value);

    if (!lessonId) {
        showErrorMessage(
            USER_EDIT_MESSAGE_ID,
            "Please select a lesson to assign."
        );

        return;
    }

    const selectedLesson =
        availableLessons.find(
            (lesson) =>
                Number(lesson.lessonId) === lessonId
        );

    if (!selectedLesson) {
        return;
    }

    assignedLessons.push(
        normalizeAvailableLesson(selectedLesson)
    );

    select.value = "";

    resetLeaveWithoutSavingConfirmation();
    renderAssignedLessonsTable();
    renderAvailableLessonsDropdown();
}


async function loadAvailableLessons() {
    const data =
        await getJson(
            LLA_API_ENDPOINTS.admin.lessons.list
        );

    if (!data.success) {
        throw new Error(
            data.error || "Failed to load lessons."
        );
    }

    availableLessons =
        data.lessons || [];

    renderAvailableLessonsDropdown();
}


async function loadAssignedLessons(userId) {
    const data =
        await getJson(
            LLA_API_ENDPOINTS.admin.userLessons.byUserId(userId)
        );

    if (!data.success) {
        throw new Error(
            data.error || "Failed to load assigned lessons."
        );
    }

    assignedLessons =
        data.userLessons || [];

    originalAssignedLessonIds =
        getAssignedLessonIds();

    renderAssignedLessonsTable();
    renderAvailableLessonsDropdown();
}


async function saveUser(event) {
    event.preventDefault();

    if (currentUserIsProtectedAdmin) {
        showInfoMessage(
            USER_EDIT_MESSAGE_ID,
            "Admin users cannot be edited."
        );

        return;
    }

    hideMessage(USER_EDIT_MESSAGE_ID);

    const userId =
        document.getElementById("userId").value;

    const payload =
        getFormData();

    if (!payload.displayName || !payload.email) {
        showErrorMessage(
            USER_EDIT_MESSAGE_ID,
            "Display name and email are required."
        );

        return;
    }

    if (!hasUserChanged(payload)) {
        showInfoMessage(
            USER_EDIT_MESSAGE_ID,
            "No changes to save."
        );

        return;
    }

    setElementDisabled(SAVE_USER_BUTTON_ID, true);
    setButtonText(SAVE_USER_BUTTON_ID, "Saving...");

    try {
        if (
            payload.displayName !== originalUserData.displayName ||
            payload.email !== originalUserData.email ||
            payload.isActive !== originalUserData.isActive ||
            payload.isVerified !== originalUserData.isVerified
        ) {
            const userResponse =
                await putJson(
                    LLA_API_ENDPOINTS.admin.users.byId(userId),
                    payload
                );

            if (!userResponse.success) {
                throw new Error(
                    userResponse.error || "Failed to update user."
                );
            }
        }

        if (haveAssignedLessonsChanged()) {
            const assignmentResponse =
                await putJson(
                    LLA_API_ENDPOINTS.admin.userLessons.byUserId(userId),
                    {
                        lessons:
                            getAssignedLessonIds().map((lessonId) => ({
                                lesson_id: lessonId
                            }))
                    }
                );

            if (!assignmentResponse.success) {
                throw new Error(
                    assignmentResponse.error ||
                    "Failed to update assigned lessons."
                );
            }
        }

        originalUserData = {
            ...payload
        };

        originalAssignedLessonIds =
            getAssignedLessonIds();

        leaveWithoutSavingConfirmed =
            false;

        renderAssignedLessonsTable();
        renderAvailableLessonsDropdown();

        showSuccessMessage(
            USER_EDIT_MESSAGE_ID,
            "User updated successfully."
        );

    } catch (error) {
        showErrorMessage(
            USER_EDIT_MESSAGE_ID,
            error.message || "Failed to save user."
        );

    } finally {
        setElementDisabled(SAVE_USER_BUTTON_ID, false);
        setButtonText(SAVE_USER_BUTTON_ID, "Save");
    }
}


async function loadUserForEdit() {
    const userId =
        getUserIdFromUrl();

    if (!userId) {
        showErrorMessage(
            USER_EDIT_MESSAGE_ID,
            "User ID is missing."
        );

        return;
    }

    setFormDisabled(USER_EDIT_FORM_ID, true);

    try {
        const data =
            await getJson(
                LLA_API_ENDPOINTS.admin.users.byId(userId)
            );

        if (!data.success || !data.user) {
            showErrorMessage(
                USER_EDIT_MESSAGE_ID,
                data.error || "User could not be found."
            );

            return;
        }

        fillEditForm(data.user);

        await loadAvailableLessons();
        await loadAssignedLessons(userId);

    } catch (error) {
        showErrorMessage(
            USER_EDIT_MESSAGE_ID,
            error.message || "Failed to load user for editing."
        );

    } finally {
        if (!currentUserIsProtectedAdmin) {
            setFormDisabled(USER_EDIT_FORM_ID, false);
        }
    }
}


document
    .getElementById(USER_EDIT_FORM_ID)
    .addEventListener("submit", saveUser);


document
    .getElementById(USER_EDIT_FORM_ID)
    .addEventListener("input", resetLeaveWithoutSavingConfirmation);


document
    .getElementById("backToUsersButton")
    .addEventListener("click", navigateBackToUsers);


document
    .getElementById(ADD_USER_BUTTON_ID)
    .addEventListener("click", navigateToUserCreate);


document
    .getElementById(DELETE_USER_BUTTON_ID)
    .addEventListener("click", () => {
        const userId =
            document.getElementById("userId").value;

        deleteUser(userId);
    });


document
    .getElementById("addLessonButton")
    .addEventListener("click", addSelectedLesson);


loadUserForEdit();