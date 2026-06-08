/*
 * Shared mobile interaction toolbar component.
 *
 * Responsibilities:
 * - Load toolbar CSS
 * - Load shared frontend path dependency
 * - Load interaction-style dependency
 * - Load toolbar HTML
 * - Delegate interaction-style switching to shared logic
 */

const MOBILE_TOOLBAR_CONTAINER_ID =
    "interaction-toolbar-container";

const MOBILE_TOOLBAR_CSS_ID =
    "mobile-interaction-toolbar-css";

const FRONTEND_PATHS_SCRIPT_ID =
    "frontend-paths-script";

const INTERACTION_STYLE_SCRIPT_ID =
    "interaction-style-script";

function loadMobileInteractionToolbarCss() {

    if (document.getElementById(MOBILE_TOOLBAR_CSS_ID)) {
        return;
    }

    const cssLink = document.createElement("link");

    cssLink.id = MOBILE_TOOLBAR_CSS_ID;
    cssLink.rel = "stylesheet";
    cssLink.href =
        "/mobile/shared/components/interaction-toolbar/interaction-toolbar.css";

    document.head.appendChild(cssLink);
}

function loadScriptOnce(scriptId, scriptPath, globalCheck) {

    return new Promise((resolve, reject) => {

        if (globalCheck()) {
            resolve();
            return;
        }

        if (document.getElementById(scriptId)) {
            resolve();
            return;
        }

        const script = document.createElement("script");

        script.id = scriptId;
        script.src = scriptPath;

        script.onload = resolve;

        script.onerror = function () {
            reject(
                new Error(`Failed to load ${scriptPath}.`)
            );
        };

        document.body.appendChild(script);
    });
}

async function loadMobileInteractionToolbarDependencies() {

    await loadScriptOnce(
        FRONTEND_PATHS_SCRIPT_ID,
        "/shared/frontend-paths.js",
        () => Boolean(window.LLA_PATHS)
    );

    await loadScriptOnce(
        INTERACTION_STYLE_SCRIPT_ID,
        "/shared/interaction-style.js",
        () => typeof switchInteractionStyle === "function"
    );
}

async function loadMobileInteractionToolbar() {

    const container =
        document.getElementById(
            MOBILE_TOOLBAR_CONTAINER_ID
        );

    if (!container) {
        return;
    }

    try {

        loadMobileInteractionToolbarCss();

        await loadMobileInteractionToolbarDependencies();

        const response = await fetch(
            "/mobile/shared/components/interaction-toolbar/interaction-toolbar.html"
        );

        if (!response.ok) {
            throw new Error(
                "Mobile interaction toolbar HTML could not be loaded."
            );
        }

        const toolbarHtml =
            await response.text();

        container.innerHTML = toolbarHtml;

        const switchToDesktopButton =
            document.getElementById(
                "switchToDesktopButton"
            );

        if (!switchToDesktopButton) {
            console.error(
                "Switch to desktop button not found."
            );

            return;
        }

        switchToDesktopButton.addEventListener(
            "click",
            () => {
                switchInteractionStyle(
                    InteractionStyle.DESKTOP
                );
            }
        );

    } catch (error) {

        console.error(
            "Failed to load mobile interaction toolbar:",
            error
        );
    }
}

document.addEventListener(
    "DOMContentLoaded",
    loadMobileInteractionToolbar
);