/*
 * Shared UI state utilities.
 *
 * Purpose:
 * Provides reusable helpers for temporarily enabling/disabling
 * buttons and form controls during asynchronous operations.
 *
 * Why this exists:
 * CRUD pages often need to prevent repeated user actions while
 * a request is running, such as:
 * - double-clicking Save
 * - clicking Delete multiple times
 * - editing form fields before data has loaded
 *
 * Keeping this logic here gives all pages the same interaction pattern.
 */

function getUiElement(elementId) {
    const element =
        document.getElementById(elementId);

    if (!element) {
        console.error(
            `UI element not found: ${elementId}`
        );

        return null;
    }

    return element;
}

function setElementDisabled(elementId, isDisabled) {
    const element =
        getUiElement(elementId);

    if (!element) {
        return;
    }

    element.disabled = isDisabled;
}

function setFormDisabled(formId, isDisabled) {
    const form =
        getUiElement(formId);

    if (!form) {
        return;
    }

    const controls =
        form.querySelectorAll("input, select, textarea, button");

    controls.forEach((control) => {
        control.disabled = isDisabled;
    });
}

function setButtonText(buttonId, text) {
    const button =
        getUiElement(buttonId);

    if (!button) {
        return;
    }

    button.textContent = text;
}