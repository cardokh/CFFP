const LEARNING_ITEM_CREATE_MESSAGE_ID =
    "learningItemCreateMessage";

const CREATE_LEARNING_ITEM_BUTTON_ID =
    "createLearningItemButton";

const CATEGORY_SELECT_ID =
    "categoryId";

const ITEM_TYPE_SELECT_ID =
    "itemType";

const LEARNING_ITEM_TYPES_CONFIG_PATH =
    "./config/learning-item-types.json";

const CREATE_LEARNING_ITEM_BUTTON_DEFAULT_TEXT =
    "Create learning item";

const CREATE_LEARNING_ITEM_BUTTON_LOADING_TEXT =
    "Creating...";

const FAILED_TO_CREATE_LEARNING_ITEM_MESSAGE =
    "Failed to create learning item.";

const FAILED_TO_LOAD_CATEGORIES_MESSAGE =
    "Failed to load lesson categories.";

const FAILED_TO_LOAD_LEARNING_ITEM_TYPES_MESSAGE =
    "Failed to load learning item types.";

const LEARNING_ITEM_CREATED_SUCCESS_MESSAGE =
    "Learning item created successfully.";

const ADMIN_UPDATED_BY =
    "admin";

let leaveWithoutSavingConfirmed =
    false;

function navigateBackToLearningItems() {
    if (!hasUnsavedChanges()) {
        window.location.href =
            LLA_PATHS.desktop.protected.admin.learningItems.list;

        return;
    }

    if (!leaveWithoutSavingConfirmed) {
        leaveWithoutSavingConfirmed =
            true;

        showInfoMessage(
            LEARNING_ITEM_CREATE_MESSAGE_ID,
            "Unsaved changes detected. Click Create learning item to save the learning item or click Back again to leave without saving."
        );

        return;
    }

    window.location.href =
        LLA_PATHS.desktop.protected.admin.learningItems.list;
}

function resetLeaveWithoutSavingConfirmation() {
    leaveWithoutSavingConfirmed =
        false;
}

function renderLearningItemTypeOptions(learningItemTypes) {
    const itemTypeSelect =
        document.getElementById(ITEM_TYPE_SELECT_ID);

    itemTypeSelect.innerHTML = `
        <option value="">Select type</option>
    `;

    learningItemTypes.forEach((learningItemType) => {
        const option =
            document.createElement("option");

        option.value =
            learningItemType.id;

        option.textContent =
            learningItemType.displayName;

        itemTypeSelect.appendChild(option);
    });
}

async function loadLearningItemTypes() {
    const response =
        await fetch(LEARNING_ITEM_TYPES_CONFIG_PATH);

    if (!response.ok) {
        throw new Error(FAILED_TO_LOAD_LEARNING_ITEM_TYPES_MESSAGE);
    }

    const learningItemTypes =
        await response.json();

    if (!Array.isArray(learningItemTypes)) {
        throw new Error(FAILED_TO_LOAD_LEARNING_ITEM_TYPES_MESSAGE);
    }

    renderLearningItemTypeOptions(learningItemTypes);
}

function renderCategoryOptions(lessonCategories) {
    const categorySelect =
        document.getElementById(CATEGORY_SELECT_ID);

    categorySelect.innerHTML = `
        <option value="">Select category</option>
    `;

    lessonCategories.forEach((category) => {
        const option =
            document.createElement("option");

        option.value =
            category.categoryId;

        option.textContent =
            category.name;

        categorySelect.appendChild(option);
    });
}

async function loadLessonCategories() {
    const data =
        await getJson(
            LLA_API_ENDPOINTS.admin.lessonCategories.list
        );

    const lessonCategories =
        data.lessonCategories;

    if (!data.success || !lessonCategories) {
        throw new Error(
            FAILED_TO_LOAD_CATEGORIES_MESSAGE
        );
    }

    renderCategoryOptions(
        lessonCategories
    );
}

function readLearningItemFormData() {
    return {
        sourceText:
            document.getElementById("sourceText").value.trim(),

        englishTranslation:
            document.getElementById("englishTranslation")
                .value
                .trim(),

        pronunciation:
            document.getElementById("pronunciation").value.trim(),

        exampleText:
            document.getElementById("exampleText").value.trim(),

        itemType:
            document.getElementById(ITEM_TYPE_SELECT_ID).value,

        categoryId:
            Number(
                document.getElementById(
                    CATEGORY_SELECT_ID
                ).value
            ),

        isActive:
            document.getElementById("isActive").checked,

        updatedBy:
            ADMIN_UPDATED_BY
    };
}

function hasUnsavedChanges() {
    const formData =
        readLearningItemFormData();

    return Boolean(
        formData.sourceText ||
        formData.englishTranslation ||
        formData.pronunciation ||
        formData.exampleText ||
        formData.itemType ||
        formData.categoryId ||
        !formData.isActive
    );
}

function clearLearningItemForm() {
    document
        .getElementById("learningItemCreateForm")
        .reset();

    document.getElementById("isActive").checked =
        true;

    leaveWithoutSavingConfirmed =
        false;
}

async function createLearningItem(event) {
    event.preventDefault();

    hideMessage(
        LEARNING_ITEM_CREATE_MESSAGE_ID
    );

    setElementDisabled(
        CREATE_LEARNING_ITEM_BUTTON_ID,
        true
    );

    setButtonText(
        CREATE_LEARNING_ITEM_BUTTON_ID,
        CREATE_LEARNING_ITEM_BUTTON_LOADING_TEXT
    );

    try {
        const payload =
            readLearningItemFormData();

        const data =
            await postJson(
                LLA_API_ENDPOINTS.admin.learningItems.create,
                payload
            );

        if (!data.success) {
            throw new Error(
                data.error ||
                FAILED_TO_CREATE_LEARNING_ITEM_MESSAGE
            );
        }

        clearLearningItemForm();

        showSuccessMessage(
            LEARNING_ITEM_CREATE_MESSAGE_ID,
            LEARNING_ITEM_CREATED_SUCCESS_MESSAGE
        );

    } catch (error) {
        console.error(error);

        showErrorMessage(
            LEARNING_ITEM_CREATE_MESSAGE_ID,
            error.message ||
            FAILED_TO_CREATE_LEARNING_ITEM_MESSAGE
        );

    } finally {
        setElementDisabled(
            CREATE_LEARNING_ITEM_BUTTON_ID,
            false
        );

        setButtonText(
            CREATE_LEARNING_ITEM_BUTTON_ID,
            CREATE_LEARNING_ITEM_BUTTON_DEFAULT_TEXT
        );
    }
}

async function initializeLearningItemCreatePage() {
    try {
        await loadLearningItemTypes();
        await loadLessonCategories();

    } catch (error) {
        console.error(error);

        showErrorMessage(
            LEARNING_ITEM_CREATE_MESSAGE_ID,
            error.message ||
            FAILED_TO_LOAD_CATEGORIES_MESSAGE
        );
    }
}

document
    .getElementById("backToLearningItemsButton")
    .addEventListener(
        "click",
        navigateBackToLearningItems
    );

document
    .getElementById("learningItemCreateForm")
    .addEventListener(
        "input",
        resetLeaveWithoutSavingConfirmation
    );

document
    .getElementById("learningItemCreateForm")
    .addEventListener(
        "submit",
        createLearningItem
    );

initializeLearningItemCreatePage();