const LESSON_CATEGORY_CREATE_MESSAGE_ID =
    "lessonCategoryCreateMessage";

const CREATE_LESSON_CATEGORY_BUTTON_ID =
    "createLessonCategoryButton";

const CREATE_LESSON_CATEGORY_BUTTON_DEFAULT_TEXT =
    "Create category";

const CREATE_LESSON_CATEGORY_BUTTON_LOADING_TEXT =
    "Creating...";

const FAILED_TO_CREATE_LESSON_CATEGORY_MESSAGE =
    "Failed to create lesson category.";

const LESSON_CATEGORY_CREATED_SUCCESS_MESSAGE =
    "Lesson category created successfully.";

const ADMIN_UPDATED_BY =
    "admin";

let leaveWithoutSavingConfirmed =
    false;

function navigateBackToLessonCategories() {
    if (!hasUnsavedChanges()) {
        window.location.href =
            LLA_PATHS.desktop.protected.admin.lessonCategories.list;

        return;
    }

    if (!leaveWithoutSavingConfirmed) {
        leaveWithoutSavingConfirmed =
            true;

        showInfoMessage(
            LESSON_CATEGORY_CREATE_MESSAGE_ID,
            "Unsaved changes detected. Click Create category to save the category or click Back again to leave without saving."
        );

        return;
    }

    window.location.href =
        LLA_PATHS.desktop.protected.admin.lessonCategories.list;
}

function resetLeaveWithoutSavingConfirmation() {
    leaveWithoutSavingConfirmed =
        false;
}

function readLessonCategoryFormData() {
    return {
        name:
            document.getElementById("name").value.trim(),

        description:
            document.getElementById("description").value.trim(),

        isActive:
            document.getElementById("isActive").checked,

        updatedBy:
            ADMIN_UPDATED_BY
    };
}

function hasUnsavedChanges() {
    const formData =
        readLessonCategoryFormData();

    return Boolean(
        formData.name ||
        formData.description ||
        !formData.isActive
    );
}

function clearLessonCategoryForm() {
    document
        .getElementById("lessonCategoryCreateForm")
        .reset();

    document.getElementById("isActive").checked =
        true;

    leaveWithoutSavingConfirmed =
        false;
}

async function createLessonCategory(event) {
    event.preventDefault();

    hideMessage(
        LESSON_CATEGORY_CREATE_MESSAGE_ID
    );

    setElementDisabled(
        CREATE_LESSON_CATEGORY_BUTTON_ID,
        true
    );

    setButtonText(
        CREATE_LESSON_CATEGORY_BUTTON_ID,
        CREATE_LESSON_CATEGORY_BUTTON_LOADING_TEXT
    );

    try {
        const payload =
            readLessonCategoryFormData();

        const data =
            await postJson(
                LLA_API_ENDPOINTS.admin.lessonCategories.create,
                payload
            );

        if (!data.success) {
            throw new Error(
                data.error ||
                FAILED_TO_CREATE_LESSON_CATEGORY_MESSAGE
            );
        }

        clearLessonCategoryForm();

        showSuccessMessage(
            LESSON_CATEGORY_CREATE_MESSAGE_ID,
            LESSON_CATEGORY_CREATED_SUCCESS_MESSAGE
        );

    } catch (error) {
        console.error(error);

        showErrorMessage(
            LESSON_CATEGORY_CREATE_MESSAGE_ID,
            error.message ||
            FAILED_TO_CREATE_LESSON_CATEGORY_MESSAGE
        );

    } finally {
        setElementDisabled(
            CREATE_LESSON_CATEGORY_BUTTON_ID,
            false
        );

        setButtonText(
            CREATE_LESSON_CATEGORY_BUTTON_ID,
            CREATE_LESSON_CATEGORY_BUTTON_DEFAULT_TEXT
        );
    }
}

document
    .getElementById("backToLessonCategoriesButton")
    .addEventListener(
        "click",
        navigateBackToLessonCategories
    );

document
    .getElementById("lessonCategoryCreateForm")
    .addEventListener(
        "input",
        resetLeaveWithoutSavingConfirmation
    );

document
    .getElementById("lessonCategoryCreateForm")
    .addEventListener(
        "submit",
        createLessonCategory
    );