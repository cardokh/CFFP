let assignedLessons = [];
let availableLessons = [];

let leaveWithoutSavingConfirmed =
    false;

const USER_CREATE_FORM_ID = "userCreateForm";

const USER_CREATE_MESSAGE_ID =
    "userCreateMessage";

const CREATE_USER_BUTTON_ID =
    "createUserButton";

const AVAILABLE_LESSON_SELECT_ID =
    "availableLessonSelect";

const ASSIGNED_LESSONS_TABLE_BODY_ID =
    "assignedLessonsTableBody";


function navigateBackToUsers() {
    if (!hasUnsavedChanges()) {
        window.location.href =
            LLA_PATHS.desktop.protected.admin.users.list;

        return;
    }

    if (!leaveWithoutSavingConfirmed) {
        leaveWithoutSavingConfirmed =
            true;

        showInfoMessage(
            USER_CREATE_MESSAGE_ID,
            "Unsaved changes detected. Click Create User to save the user or click Back again to leave without saving."
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


function getFormData() {
    return {
        displayName:
            document.getElementById("displayName").value.trim(),

        email:
            document.getElementById("email").value.trim(),

        password:
            document.getElementById("password").value,

        confirmPassword:
            document.getElementById("confirmPassword").value,

        isActive:
            document.getElementById("isActive").checked,

        isVerified:
            document.getElementById("isVerified").checked
    };
}


function hasUnsavedChanges() {
    const formData =
        getFormData();

    return Boolean(
        formData.displayName ||
        formData.email ||
        formData.password ||
        formData.confirmPassword ||
        !formData.isActive ||
        formData.isVerified ||
        assignedLessons.length > 0
    );
}


function validateFormData(formData) {
    if (
        !formData.displayName ||
        !formData.email ||
        !formData.password ||
        !formData.confirmPassword
    ) {
        return "All fields are required.";
    }

    if (formData.password !== formData.confirmPassword) {
        return "Passwords do not match.";
    }

    return null;
}


function getAssignedLessonIds() {
    return assignedLessons.map(
        (lesson) => Number(lesson.lessonId)
    );
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

    setElementDisabled(
        AVAILABLE_LESSON_SELECT_ID,
        selectableLessons.length === 0
    );

    setElementDisabled(
        "addLessonButton",
        selectableLessons.length === 0
    );
}


function removeAssignedLesson(lessonId) {
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
                        title="Remove lesson">
                        🗑
                    </button>
                </td>
            </tr>
        `).join("");
}


function addSelectedLesson() {
    const select =
        document.getElementById(
            AVAILABLE_LESSON_SELECT_ID
        );

    const lessonId =
        Number(select.value);

    if (!lessonId) {
        showErrorMessage(
            USER_CREATE_MESSAGE_ID,
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
    try {
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

    } catch (error) {
        showErrorMessage(
            USER_CREATE_MESSAGE_ID,
            error.message || "Failed to load lessons."
        );
    }
}


function resetCreateUserForm() {
    document
        .getElementById(USER_CREATE_FORM_ID)
        .reset();

    document
        .getElementById("isActive").checked = true;

    assignedLessons = [];

    leaveWithoutSavingConfirmed =
        false;

    renderAssignedLessonsTable();
    renderAvailableLessonsDropdown();
}


async function createUser(event) {
    event.preventDefault();

    hideMessage(USER_CREATE_MESSAGE_ID);

    const formData =
        getFormData();

    const validationError =
        validateFormData(formData);

    if (validationError) {
        showErrorMessage(
            USER_CREATE_MESSAGE_ID,
            validationError
        );

        return;
    }

    setElementDisabled(CREATE_USER_BUTTON_ID, true);

    setButtonText(
        CREATE_USER_BUTTON_ID,
        "Creating..."
    );

    try {
        const data =
            await postJson(
                LLA_API_ENDPOINTS.auth.register,
                formData
            );

        if (!data.success) {
            throw new Error(
                data.error || "Failed to create user."
            );
        }

        const createdUser =
            data.user;

        if (
            createdUser &&
            createdUser.userId &&
            assignedLessons.length > 0
        ) {
            const assignmentResponse =
                await putJson(
                    LLA_API_ENDPOINTS.admin.userLessons.byUserId(
                        createdUser.userId
                    ),
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
                    "Failed to assign lessons."
                );
            }
        }

        showSuccessMessage(
            USER_CREATE_MESSAGE_ID,
            "User created successfully."
        );

        resetCreateUserForm();

    } catch (error) {
        showErrorMessage(
            USER_CREATE_MESSAGE_ID,
            error.message || "Failed to create user."
        );

    } finally {

        setElementDisabled(
            CREATE_USER_BUTTON_ID,
            false
        );

        setButtonText(
            CREATE_USER_BUTTON_ID,
            "Create User"
        );
    }
}


document
    .getElementById(USER_CREATE_FORM_ID)
    .addEventListener("submit", createUser);


document
    .getElementById(USER_CREATE_FORM_ID)
    .addEventListener("input", resetLeaveWithoutSavingConfirmation);


document
    .getElementById("backToUsersButton")
    .addEventListener("click", navigateBackToUsers);


document
    .getElementById("addLessonButton")
    .addEventListener("click", addSelectedLesson);


loadAvailableLessons();