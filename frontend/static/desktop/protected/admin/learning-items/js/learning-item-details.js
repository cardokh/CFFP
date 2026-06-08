const LEARNING_ITEM_DETAILS_MESSAGE_ID =
    "learningItemDetailsMessage";

const DELETE_LEARNING_ITEM_BUTTON_ID =
    "deleteLearningItemButton";

const DELETE_LEARNING_ITEM_BUTTON_DEFAULT_TEXT =
    "Delete learning item";

const DELETE_LEARNING_ITEM_BUTTON_LOADING_TEXT =
    "Deleting...";

const CONFIRM_DELETE_LEARNING_ITEM_MESSAGE =
    "Are you sure you want to delete this learning item?";

const LEARNING_ITEM_ID_MISSING_MESSAGE =
    "Learning item ID is missing.";

const LEARNING_ITEM_NOT_FOUND_MESSAGE =
    "Learning item not found.";

const FAILED_TO_DELETE_LEARNING_ITEM_MESSAGE =
    "Failed to delete learning item.";

const FAILED_TO_LOAD_LEARNING_ITEM_DETAILS_MESSAGE =
    "Failed to load learning item details.";

function getLearningItemIdFromUrl() {
    const params =
        new URLSearchParams(window.location.search);

    return params.get("learningItemId");
}

function navigateToLearningItemEdit(learningItemId) {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.learningItems.edit(learningItemId);
}

function navigateBackToLearningItems() {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.learningItems.list;
}

async function deleteLearningItem(learningItemId) {
    const confirmed =
        confirm(CONFIRM_DELETE_LEARNING_ITEM_MESSAGE);

    if (!confirmed) {
        return;
    }

    hideMessage(LEARNING_ITEM_DETAILS_MESSAGE_ID);

    setElementDisabled(
        DELETE_LEARNING_ITEM_BUTTON_ID,
        true
    );

    setButtonText(
        DELETE_LEARNING_ITEM_BUTTON_ID,
        DELETE_LEARNING_ITEM_BUTTON_LOADING_TEXT
    );

    try {
        const data =
            await deleteJson(
                LLA_API_ENDPOINTS.admin.learningItems.byId(learningItemId)
            );

        if (!data.success) {
            throw new Error(
                data.error ||
                FAILED_TO_DELETE_LEARNING_ITEM_MESSAGE
            );
        }

        navigateBackToLearningItems();

    } catch (error) {
        console.error(error);

        showErrorMessage(
            LEARNING_ITEM_DETAILS_MESSAGE_ID,
            error.message ||
            FAILED_TO_DELETE_LEARNING_ITEM_MESSAGE
        );

        setElementDisabled(
            DELETE_LEARNING_ITEM_BUTTON_ID,
            false
        );

        setButtonText(
            DELETE_LEARNING_ITEM_BUTTON_ID,
            DELETE_LEARNING_ITEM_BUTTON_DEFAULT_TEXT
        );
    }
}

function formatBoolean(value) {
    return value ? "Yes" : "No";
}

function renderLearningItem(learningItem) {
    const card =
        document.getElementById("learningItemDetailsCard");

    card.innerHTML = `
        <div class="learning-item-details-grid">

            <div class="learning-item-details-row learning-item-details-row-primary">

                <div class="learning-item-detail-item">
                    <span class="learning-item-detail-label">ID</span>
                    <span class="learning-item-detail-value">
                        ${escapeHtml(learningItem.itemId)}
                    </span>
                </div>

                <div class="learning-item-detail-item">
                    <span class="learning-item-detail-label">Type</span>
                    <span class="learning-item-detail-value">
                        ${escapeHtml(learningItem.itemType || "")}
                    </span>
                </div>

                <div class="learning-item-detail-item">
                    <span class="learning-item-detail-label">Category</span>
                    <span class="learning-item-detail-value">
                        ${escapeHtml(learningItem.categoryName || "")}
                    </span>
                </div>

                <div class="learning-item-detail-item">
                    <span class="learning-item-detail-label">Active</span>
                    <span class="learning-item-detail-value">
                        ${formatBoolean(learningItem.isActive)}
                    </span>
                </div>

            </div>

            <div class="learning-item-details-row learning-item-details-row-language">

                <div class="learning-item-detail-item">
                    <span class="learning-item-detail-label">Swedish</span>
                    <span class="learning-item-detail-value multiline">
                        ${escapeHtml(learningItem.sourceText || "")}
                    </span>
                </div>

                <div class="learning-item-detail-item">
                    <span class="learning-item-detail-label">English</span>
                    <span class="learning-item-detail-value multiline">
                        ${escapeHtml(learningItem.englishTranslation || "")}
                    </span>
                </div>

            </div>

            <div class="learning-item-details-row learning-item-details-row-learning-support">

                <div class="learning-item-detail-item">
                    <span class="learning-item-detail-label">Pronunciation</span>
                    <span class="learning-item-detail-value multiline">
                        ${escapeHtml(learningItem.pronunciation || "")}
                    </span>
                </div>

                <div class="learning-item-detail-item">
                    <span class="learning-item-detail-label">Example sentence</span>
                    <span class="learning-item-detail-value multiline">
                        ${escapeHtml(learningItem.exampleText || "")}
                    </span>
                </div>

            </div>

            <div class="learning-item-details-row learning-item-details-row-audit">

                <div class="learning-item-detail-item">
                    <span class="learning-item-detail-label">Created at</span>
                    <span class="learning-item-detail-value">
                        ${escapeHtml(learningItem.createdAt || "")}
                    </span>
                </div>

                <div class="learning-item-detail-item">
                    <span class="learning-item-detail-label">Updated at</span>
                    <span class="learning-item-detail-value">
                        ${escapeHtml(learningItem.updatedAt || "")}
                    </span>
                </div>

                <div class="learning-item-detail-item">
                    <span class="learning-item-detail-label">Updated by</span>
                    <span class="learning-item-detail-value">
                        ${escapeHtml(learningItem.updatedBy || "")}
                    </span>
                </div>

            </div>

        </div>
    `;
}

function setupLearningItemActionButtons(learningItemId) {
    document
        .getElementById("editLearningItemButton")
        .addEventListener("click", () => {
            navigateToLearningItemEdit(learningItemId);
        });

    document
        .getElementById(DELETE_LEARNING_ITEM_BUTTON_ID)
        .addEventListener("click", () => {
            deleteLearningItem(learningItemId);
        });
}

async function loadLearningItemDetails() {
    const learningItemId =
        getLearningItemIdFromUrl();

    const card =
        document.getElementById("learningItemDetailsCard");

    if (!learningItemId) {
        card.innerHTML = `
            <p>${escapeHtml(LEARNING_ITEM_ID_MISSING_MESSAGE)}</p>
        `;

        return;
    }

    try {
        const data =
            await getJson(
                LLA_API_ENDPOINTS.admin.learningItems.byId(learningItemId)
            );

        if (!data.success || !data.learningItem) {
            card.innerHTML = `
                <p>
                    ${escapeHtml(
                data.error ||
                LEARNING_ITEM_NOT_FOUND_MESSAGE
            )}
                </p>
            `;

            return;
        }

        renderLearningItem(data.learningItem);

        setupLearningItemActionButtons(learningItemId);

    } catch (error) {
        console.error(error);

        card.innerHTML = `
            <p>
                ${escapeHtml(
            FAILED_TO_LOAD_LEARNING_ITEM_DETAILS_MESSAGE
        )}
            </p>
        `;
    }
}

document
    .getElementById("backToLearningItemsButton")
    .addEventListener("click", navigateBackToLearningItems);

loadLearningItemDetails();