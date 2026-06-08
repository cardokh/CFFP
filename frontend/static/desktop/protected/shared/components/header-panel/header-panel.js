/*
 * Shared protected header panel component.
 *
 * Responsibilities:
 * - Load reusable protected desktop header panel.
 * - Provide consistent student UX across protected pages.
 * - Render lightweight animated HRI/language-learning UI.
 * - Display the currently authenticated user's name.
 *
 * Architectural rules:
 * - Protected pages should reuse this component.
 * - Protected pages should not duplicate header-panel markup.
 * - The greeting must come from the authenticated frontend session.
 */

const HEADER_PANEL_CSS_ID =
    "header-panel-css";

const HEADER_PANEL_GREETING_ID =
    "studentTopPanelGreeting";


function escapeHeaderPanelHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function getHeaderPanelDisplayName() {
    const authenticatedUser =
        getAuthenticatedUser();

    return (
        authenticatedUser?.displayName ||
        "User"
    );
}


function loadHeaderPanelStyles() {
    if (
        document.getElementById(
            HEADER_PANEL_CSS_ID
        )
    ) {
        return;
    }

    const cssLink =
        document.createElement("link");

    cssLink.id =
        HEADER_PANEL_CSS_ID;

    cssLink.rel =
        "stylesheet";

    cssLink.href =
        "/desktop/protected/shared/components/header-panel/header-panel.css";

    document.head.appendChild(cssLink);
}


function renderHeaderPanelGreeting() {
    const greetingElement =
        document.getElementById(
            HEADER_PANEL_GREETING_ID
        );

    if (!greetingElement) {
        return;
    }

    greetingElement.innerHTML =
        `Hej ${escapeHeaderPanelHtml(
            getHeaderPanelDisplayName()
        )}! 👋`;
}


async function loadHeaderPanel() {

    const container =
        document.getElementById(
            "header-panel-container"
        );

    if (!container) {
        console.error(
            "Header panel container not found."
        );

        return;
    }

    try {
        loadHeaderPanelStyles();

        const response =
            await fetch(
                "/desktop/protected/shared/components/header-panel/header-panel.html"
            );

        if (!response.ok) {
            throw new Error(
                "Header panel HTML could not be loaded."
            );
        }

        const html =
            await response.text();

        container.innerHTML =
            html;

        renderHeaderPanelGreeting();

    } catch (error) {
        console.error(
            "Failed to load header panel:",
            error
        );
    }
}