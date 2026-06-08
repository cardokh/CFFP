const LEARNING_ITEM_EDIT_MESSAGE_ID =
    "learningItemEditMessage";

const SAVE_LEARNING_ITEM_BUTTON_ID =
    "saveLearningItemButton";

const DELETE_LEARNING_ITEM_BUTTON_ID =
    "deleteLearningItemButton";

const CATEGORY_SELECT_ID =
    "categoryId";

const ITEM_TYPE_SELECT_ID =
    "itemType";

const LEARNING_ITEM_TYPES_CONFIG_PATH =
    "./config/learning-item-types.json";

const SAVE_LEARNING_ITEM_BUTTON_DEFAULT_TEXT =
    "Save";

const SAVE_LEARNING_ITEM_BUTTON_LOADING_TEXT =
    "Saving...";

const LEARNING_ITEM_ID_MISSING_MESSAGE =
    "Learning item ID is missing.";

const LEARNING_ITEM_NOT_FOUND_MESSAGE =
    "Learning item not found.";

const FAILED_TO_LOAD_LEARNING_ITEM_MESSAGE =
    "Failed to load learning item.";

const FAILED_TO_LOAD_CATEGORIES_MESSAGE =
    "Failed to load lesson categories.";

const FAILED_TO_LOAD_LEARNING_ITEM_TYPES_MESSAGE =
    "Failed to load learning item types.";

const FAILED_TO_UPDATE_LEARNING_ITEM_MESSAGE =
    "Failed to update learning item.";

const FAILED_TO_DELETE_LEARNING_ITEM_MESSAGE =
    "Failed to delete learning item.";

const LEARNING_ITEM_UPDATED_SUCCESS_MESSAGE =
    "Learning item updated successfully.";

const NO_CHANGES_DETECTED_MESSAGE =
    "No changes detected.";

const ADMIN_UPDATED_BY =
    "admin";

let originalLearningItemFormData =
    null;

let leaveWithoutSavingConfirmed =
    false;

function getLearningItemIdFromUrl() {
    const params =
        new URLSearchParams(window.location.search);

    return params.get("learningItemId");
}

function navigateBackToLearningItems() {
    const hasChanges =
        hasLearningItemFormChanged(
            readLearningItemFormData()
        );

    if (!hasChanges) {
        window.location.href =
            LLA_PATHS.desktop.protected.admin.learningItems.list;

        return;
    }

    if (!leaveWithoutSavingConfirmed) {
        leaveWithoutSavingConfirmed =
            true;

        showInfoMessage(
            LEARNING_ITEM_EDIT_MESSAGE_ID,
            "Unsaved changes detected. Click Save to apply your changes or click Back again to leave without saving."
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
        throw new Error(
            FAILED_TO_LOAD_LEARNING_ITEM_TYPES_MESSAGE
        );
    }

    const learningItemTypes =
        await response.json();

    if (!Array.isArray(learningItemTypes)) {
        throw new Error(
            FAILED_TO_LOAD_LEARNING_ITEM_TYPES_MESSAGE
        );
    }

    renderLearningItemTypeOptions(
        learningItemTypes
    );
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

function populateLearningItemForm(learningItem) {
    document.getElementById("learningItemId").value =
        learningItem.itemId;

    document.getElementById("learningItemIdDisplay").value =
        learningItem.itemId;

    document.getElementById("sourceText").value =
        learningItem.sourceText || "";

    document.getElementById("englishTranslation").value =
        learningItem.englishTranslation || "";

    document.getElementById("pronunciation").value =
        learningItem.pronunciation || "";

    document.getElementById("exampleText").value =
        learningItem.exampleText || "";

    document.getElementById(ITEM_TYPE_SELECT_ID).value =
        learningItem.itemType || "";

    document.getElementById(CATEGORY_SELECT_ID).value =
        learningItem.categoryId || "";

    document.getElementById("isActive").checked =
        Boolean(learningItem.isActive);
}

function readLearningItemFormData() {
    return {
        sourceText:
            document.getElementById("sourceText").value.trim(),

        englishTranslation:
            document
                .getElementById("englishTranslation")
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
                document.getElementById(CATEGORY_SELECT_ID).value
            ),

        isActive:
            document.getElementById("isActive").checked,

        updatedBy:
            ADMIN_UPDATED_BY
    };
}

function normalizeLearningItemFormDataForComparison(formData) {
    return {
        sourceText: formData.sourceText || "",
        englishTranslation: formData.englishTranslation || "",
        pronunciation: formData.pronunciation || "",
        exampleText: formData.exampleText || "",
        itemType: formData.itemType || "",
        categoryId: Number(formData.categoryId),
        isActive: Boolean(formData.isActive)
    };
}

function hasLearningItemFormChanged(currentFormData) {
    if (!originalLearningItemFormData) {
        return false;
    }

    return JSON.stringify(
        normalizeLearningItemFormDataForComparison(currentFormData)
    ) !== JSON.stringify(
        normalizeLearningItemFormDataForComparison(originalLearningItemFormData)
    );
}

function storeOriginalLearningItemFormData() {
    originalLearningItemFormData =
        readLearningItemFormData();
}

async function loadLearningItemForEdit() {
    const learningItemId =
        getLearningItemIdFromUrl();

    if (!learningItemId) {
        showErrorMessage(
            LEARNING_ITEM_EDIT_MESSAGE_ID,
            LEARNING_ITEM_ID_MISSING_MESSAGE
        );

        return;
    }

    try {
        await loadLearningItemTypes();
        await loadLessonCategories();

        const data =
            await getJson(
                LLA_API_ENDPOINTS.admin.learningItems.byId(learningItemId)
            );

        if (!data.success || !data.learningItem) {
            showErrorMessage(
                LEARNING_ITEM_EDIT_MESSAGE_ID,
                data.error || LEARNING_ITEM_NOT_FOUND_MESSAGE
            );

            return;
        }

        populateLearningItemForm(data.learningItem);

        storeOriginalLearningItemFormData();

    } catch (error) {
        console.error(error);

        showErrorMessage(
            LEARNING_ITEM_EDIT_MESSAGE_ID,
            error.message || FAILED_TO_LOAD_LEARNING_ITEM_MESSAGE
        );
    }
}

async function deleteLearningItem() {
    const learningItemId =
        getLearningItemIdFromUrl();

    if (!learningItemId) {
        showErrorMessage(
            LEARNING_ITEM_EDIT_MESSAGE_ID,
            LEARNING_ITEM_ID_MISSING_MESSAGE
        );

        return;
    }

    const confirmed =
        confirm("Are you sure you want to delete this learning item?");

    if (!confirmed) {
        return;
    }

    hideMessage(LEARNING_ITEM_EDIT_MESSAGE_ID);

    setElementDisabled(
        DELETE_LEARNING_ITEM_BUTTON_ID,
        true
    );

    setElementDisabled(
        SAVE_LEARNING_ITEM_BUTTON_ID,
        true
    );

    setButtonText(
        DELETE_LEARNING_ITEM_BUTTON_ID,
        "Deleting..."
    );

    try {
        const data =
            await deleteJson(
                LLA_API_ENDPOINTS.admin.learningItems.byId(learningItemId)
            );

        if (!data.success) {
            throw new Error(
                data.error || FAILED_TO_DELETE_LEARNING_ITEM_MESSAGE
            );
        }

        window.location.href =
            LLA_PATHS.desktop.protected.admin.learningItems.list;

    } catch (error) {
        console.error(error);

        showErrorMessage(
            LEARNING_ITEM_EDIT_MESSAGE_ID,
            error.message || FAILED_TO_DELETE_LEARNING_ITEM_MESSAGE
        );

        setElementDisabled(
            DELETE_LEARNING_ITEM_BUTTON_ID,
            false
        );

        setElementDisabled(
            SAVE_LEARNING_ITEM_BUTTON_ID,
            false
        );

        setButtonText(
            DELETE_LEARNING_ITEM_BUTTON_ID,
            "Delete"
        );
    }
}

async function saveLearningItem(event) {
    event.preventDefault();

    const learningItemId =
        getLearningItemIdFromUrl();

    if (!learningItemId) {
        showErrorMessage(
            LEARNING_ITEM_EDIT_MESSAGE_ID,
            LEARNING_ITEM_ID_MISSING_MESSAGE
        );

        return;
    }

    hideMessage(LEARNING_ITEM_EDIT_MESSAGE_ID);

    const payload =
        readLearningItemFormData();

    if (!hasLearningItemFormChanged(payload)) {
        showInfoMessage(
            LEARNING_ITEM_EDIT_MESSAGE_ID,
            NO_CHANGES_DETECTED_MESSAGE
        );

        return;
    }

    setElementDisabled(
        SAVE_LEARNING_ITEM_BUTTON_ID,
        true
    );

    setElementDisabled(
        DELETE_LEARNING_ITEM_BUTTON_ID,
        true
    );

    setButtonText(
        SAVE_LEARNING_ITEM_BUTTON_ID,
        SAVE_LEARNING_ITEM_BUTTON_LOADING_TEXT
    );

    try {
        const data =
            await putJson(
                LLA_API_ENDPOINTS.admin.learningItems.byId(learningItemId),
                payload
            );

        if (!data.success) {
            throw new Error(
                data.error || FAILED_TO_UPDATE_LEARNING_ITEM_MESSAGE
            );
        }

        originalLearningItemFormData =
            payload;

        leaveWithoutSavingConfirmed =
            false;

        showSuccessMessage(
            LEARNING_ITEM_EDIT_MESSAGE_ID,
            LEARNING_ITEM_UPDATED_SUCCESS_MESSAGE
        );

    } catch (error) {
        console.error(error);

        showErrorMessage(
            LEARNING_ITEM_EDIT_MESSAGE_ID,
            error.message || FAILED_TO_UPDATE_LEARNING_ITEM_MESSAGE
        );

    } finally {
        setElementDisabled(
            SAVE_LEARNING_ITEM_BUTTON_ID,
            false
        );

        setElementDisabled(
            DELETE_LEARNING_ITEM_BUTTON_ID,
            false
        );

        setButtonText(
            SAVE_LEARNING_ITEM_BUTTON_ID,
            SAVE_LEARNING_ITEM_BUTTON_DEFAULT_TEXT
        );
    }
}

document
    .getElementById("backToLearningItemsButton")
    .addEventListener("click", navigateBackToLearningItems);

document
    .getElementById(DELETE_LEARNING_ITEM_BUTTON_ID)
    .addEventListener("click", deleteLearningItem);

document
    .getElementById("learningItemEditForm")
    .addEventListener("input", resetLeaveWithoutSavingConfirmation);

document
    .getElementById("learningItemEditForm")
    .addEventListener("submit", saveLearningItem);

loadLearningItemForEdit();