/*
 * Shared UI message utilities.
 *
 * Purpose:
 * Provides one reusable way to show and hide user-facing messages
 * across forms and CRUD pages.
 *
 * Why this exists:
 * Several pages need the same message behavior:
 * - show success messages
 * - show validation errors
 * - show informational messages
 * - hide/reset messages
 *
 * Keeping this logic here avoids duplicating show/hide message code
 * in every controller file.
 *
 * Expected HTML:
 * The target element should usually have the class "form-message".
 *
 * Example:
 * <div id="userEditMessage" class="form-message hidden"></div>
 */

function getMessageElement(elementId) {
    const element =
        document.getElementById(elementId);

    if (!element) {
        console.error(
            `Message element not found: ${elementId}`
        );

        return null;
    }

    return element;
}

function showMessage(elementId, message, type = "info") {
    const element =
        getMessageElement(elementId);

    if (!element) {
        return;
    }

    element.textContent = message;
    element.className = `form-message ${type}`;
}

function hideMessage(elementId) {
    const element =
        getMessageElement(elementId);

    if (!element) {
        return;
    }

    element.textContent = "";
    element.className = "form-message hidden";
}

function showSuccessMessage(elementId, message) {
    showMessage(elementId, message, "success");
}

function showErrorMessage(elementId, message) {
    showMessage(elementId, message, "error");
}

function showInfoMessage(elementId, message) {
    showMessage(elementId, message, "info");
}