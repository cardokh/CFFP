/*
 * Shared frontend session management utilities.
 *
 * Responsibilities:
 * - Store and retrieve the authenticated frontend user session.
 * - Clear frontend session state during logout.
 * - Redirect unauthenticated users away from protected pages.
 * - Provide one reusable authentication/session guard.
 *
 * Dependencies:
 * - frontend-paths.js must be loaded before this file.
 * - interaction-style.js must be loaded before this file.
 *
 * Architectural rules:
 * - Page controllers must not access auth localStorage keys directly.
 * - Page controllers must use saveAuthenticatedUser(),
 *   getAuthenticatedUser(),
 *   requireAuthentication(),
 *   or logoutUser().
 */

const LLA_SESSION_STORAGE_KEYS = {
    user: "user"
};

function getApplicationStartPagePath() {
    if (window.LLA_PATHS && window.LLA_PATHS.root.index) {
        return window.LLA_PATHS.root.index;
    }

    return "/index.html";
}

function redirectToApplicationStartPage() {
    window.location.href =
        getApplicationStartPagePath();
}

function clearAuthenticatedUser() {
    localStorage.removeItem(
        LLA_SESSION_STORAGE_KEYS.user
    );
}

function saveAuthenticatedUser(user) {
    localStorage.setItem(
        LLA_SESSION_STORAGE_KEYS.user,
        JSON.stringify(user)
    );
}

function clearFrontendSession() {
    clearAuthenticatedUser();

    if (typeof clearInteractionStyle !== "function") {
        console.error(
            "clearInteractionStyle is unavailable. Load interaction-style.js before session-manager.js."
        );

        return;
    }

    clearInteractionStyle();
}

function logoutUser() {
    clearFrontendSession();

    redirectToApplicationStartPage();
}

function getAuthenticatedUser() {
    const storedUser =
        localStorage.getItem(
            LLA_SESSION_STORAGE_KEYS.user
        );

    if (!storedUser) {
        return null;
    }

    try {
        return JSON.parse(storedUser);

    } catch (error) {
        clearFrontendSession();

        return null;
    }
}

function requireAuthentication() {
    const authenticatedUser =
        getAuthenticatedUser();

    if (!authenticatedUser) {
        logoutUser();

        return null;
    }

    return authenticatedUser;
}