/*
 * Interaction style management.
 *
 * Responsibilities:
 * - Store the selected interaction style.
 * - Persist the selected interaction style during the browser session.
 * - Support switching between desktop and mobile interfaces.
 * - Preserve the current page context during interaction style changes.
 *
 * Dependencies:
 * - frontend-paths.js must be loaded before this file.
 *
 * Architectural rules:
 * - Controllers should not directly manipulate interaction style session state.
 * - Controllers should use switchInteractionStyle().
 */

const INTERACTION_STYLE_STORAGE_KEY = "interactionStyle";

const InteractionStyle = Object.freeze({
    MOBILE: "mobile",
    DESKTOP: "desktop"
});

const FrontendPageArea = Object.freeze({
    PUBLIC: "public",
    PROTECTED: "protected"
});

function getInteractionStyle() {
    return sessionStorage.getItem(
        INTERACTION_STYLE_STORAGE_KEY
    );
}

function setInteractionStyle(style) {
    const validStyles =
        Object.values(InteractionStyle);

    if (!validStyles.includes(style)) {
        console.error(
            "Invalid interaction style:",
            style
        );

        return;
    }

    sessionStorage.setItem(
        INTERACTION_STYLE_STORAGE_KEY,
        style
    );
}

function clearInteractionStyle() {
    sessionStorage.removeItem(
        INTERACTION_STYLE_STORAGE_KEY
    );
}

function getCurrentPageName() {
    const pathParts =
        window.location.pathname.split("/");

    const currentPage =
        pathParts[pathParts.length - 1];

    if (currentPage) {
        return currentPage;
    }

    return "login.html";
}

function getCurrentPageArea() {
    const path =
        window.location.pathname;

    if (path.includes("/protected/")) {
        return FrontendPageArea.PROTECTED;
    }

    return FrontendPageArea.PUBLIC;
}

function getInteractionStyleBasePath(style) {
    if (!window.LLA_PATHS) {
        console.error(
            "LLA_PATHS is not loaded. Load frontend-paths.js first."
        );

        return null;
    }

    const area =
        getCurrentPageArea();

    if (
        style === InteractionStyle.MOBILE &&
        area === FrontendPageArea.PROTECTED
    ) {
        return window.LLA_PATHS.mobile.protected.root;
    }

    if (
        style === InteractionStyle.MOBILE &&
        area === FrontendPageArea.PUBLIC
    ) {
        return window.LLA_PATHS.mobile.public.root;
    }

    if (
        style === InteractionStyle.DESKTOP &&
        area === FrontendPageArea.PROTECTED
    ) {
        return window.LLA_PATHS.desktop.protected.root;
    }

    if (
        style === InteractionStyle.DESKTOP &&
        area === FrontendPageArea.PUBLIC
    ) {
        return window.LLA_PATHS.desktop.public.root;
    }

    console.error(
        "Invalid interaction style:",
        style
    );

    return null;
}

function switchInteractionStyle(targetStyle) {
    setInteractionStyle(targetStyle);

    const basePath =
        getInteractionStyleBasePath(targetStyle);

    if (!basePath) {
        return;
    }

    const currentPage =
        getCurrentPageName();

    window.location.href =
        `${basePath}/${currentPage}`;
}