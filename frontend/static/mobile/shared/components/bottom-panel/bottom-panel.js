/*
 * Shared mobile bottom panel component.
 *
 * Responsibilities:
 * - Load bottom panel CSS.
 * - Load shared frontend dependencies.
 * - Load bottom panel HTML.
 * - Handle protected mobile navigation.
 * - Delegate interaction-style switching to shared logic.
 * - Delegate logout/session cleanup to shared session utilities.
 */

const MOBILE_BOTTOM_PANEL_CSS_ID =
    "mobile-bottom-panel-css";

const FRONTEND_PATHS_SCRIPT_ID =
    "frontend-paths-script";

const INTERACTION_STYLE_SCRIPT_ID =
    "interaction-style-script";

const SESSION_MANAGER_SCRIPT_ID =
    "session-manager-script";

function loadMobileBottomPanelStyles() {
    if (
        document.getElementById(
            MOBILE_BOTTOM_PANEL_CSS_ID
        )
    ) {
        return;
    }

    const cssLink =
        document.createElement("link");

    cssLink.id =
        MOBILE_BOTTOM_PANEL_CSS_ID;

    cssLink.rel =
        "stylesheet";

    cssLink.href =
        "/mobile/shared/components/bottom-panel/bottom-panel.css";

    document.head.appendChild(cssLink);
}

function loadScriptOnce(
    scriptId,
    scriptPath,
    globalCheck
) {
    return new Promise((resolve, reject) => {
        if (globalCheck()) {
            resolve();
            return;
        }

        if (document.getElementById(scriptId)) {
            resolve();
            return;
        }

        const script =
            document.createElement("script");

        script.id =
            scriptId;

        script.src =
            scriptPath;

        script.onload =
            resolve;

        script.onerror =
            function () {
                reject(
                    new Error(
                        `Failed to load ${scriptPath}.`
                    )
                );
            };

        document.body.appendChild(script);
    });
}

async function loadMobileBottomPanelDependencies() {
    await loadScriptOnce(
        FRONTEND_PATHS_SCRIPT_ID,
        "/shared/frontend-paths.js",
        () => Boolean(window.LLA_PATHS)
    );

    await loadScriptOnce(
        INTERACTION_STYLE_SCRIPT_ID,
        "/shared/interaction-style.js",
        () =>
            typeof switchInteractionStyle ===
            "function"
    );

    await loadScriptOnce(
        SESSION_MANAGER_SCRIPT_ID,
        "/shared/session-manager.js",
        () => typeof logoutUser === "function"
    );
}

async function loadMobileBottomPanel(config = {}) {
    const container =
        document.getElementById(
            "mobile-bottom-panel-container"
        );

    if (!container) {
        console.error(
            "Mobile bottom panel container not found."
        );

        return;
    }

    try {
        loadMobileBottomPanelStyles();

        await loadMobileBottomPanelDependencies();

        const response =
            await fetch(
                "/mobile/shared/components/bottom-panel/bottom-panel.html"
            );

        if (!response.ok) {
            throw new Error(
                "Mobile bottom panel HTML could not be loaded."
            );
        }

        const html =
            await response.text();

        container.innerHTML =
            html;

        setupMobileBottomPanelEvents(config);

    } catch (error) {
        console.error(
            "Failed to load mobile bottom panel:",
            error
        );
    }
}

function setupMobileBottomPanelEvents(config = {}) {
    const homeButton =
        document.getElementById(
            "mobileHomeButton"
        );

    const settingsButton =
        document.getElementById(
            "mobileSettingsButton"
        );

    const desktopButton =
        document.getElementById(
            "mobileSwitchViewButton"
        );

    const logoutButton =
        document.getElementById(
            "mobileLogoutButton"
        );

    if (homeButton) {
        homeButton.addEventListener(
            "click",
            () => {
                window.location.href =
                    window.LLA_PATHS.mobile.protected.welcome;
            }
        );
    }

    if (settingsButton) {
        settingsButton.addEventListener(
            "click",
            () => {
                window.location.href =
                    window.LLA_PATHS.mobile.protected.settings;
            }
        );
    }

    if (desktopButton) {
        desktopButton.addEventListener(
            "click",
            () => {
                switchInteractionStyle(
                    InteractionStyle.DESKTOP
                );

                window.location.href =
                    config.desktopTarget ||
                    window.LLA_PATHS.desktop.protected.welcome;
            }
        );
    }

    if (logoutButton) {
        logoutButton.addEventListener(
            "click",
            () => {
                logoutUser();
            }
        );
    }
}