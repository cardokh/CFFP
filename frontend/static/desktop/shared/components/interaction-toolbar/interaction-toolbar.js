/*
 * Shared desktop public interaction toolbar component.
 *
 * Responsibilities:
 * - Load toolbar CSS
 * - Load shared frontend path dependency
 * - Load interaction-style dependency
 * - Load toolbar HTML
 * - Delegate interaction-style switching to shared logic
 */

const INTERACTION_TOOLBAR_CSS_ID =
    "desktop-interaction-toolbar-css";

const FRONTEND_PATHS_SCRIPT_ID =
    "frontend-paths-script";

const INTERACTION_STYLE_SCRIPT_ID =
    "interaction-style-script";

function loadInteractionToolbarStyles() {
    if (document.getElementById(INTERACTION_TOOLBAR_CSS_ID)) {
        return;
    }

    const cssLink = document.createElement("link");

    cssLink.id = INTERACTION_TOOLBAR_CSS_ID;
    cssLink.rel = "stylesheet";
    cssLink.href =
        "/desktop/shared/components/interaction-toolbar/interaction-toolbar.css";

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
            reject(new Error(`Failed to load ${scriptPath}.`));
        };

        document.body.appendChild(script);
    });
}

async function loadInteractionToolbarDependencies() {
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

async function loadInteractionToolbar(activePage) {
    const toolbarContainer =
        document.getElementById("interaction-toolbar-container");

    if (!toolbarContainer) {
        console.error("Interaction toolbar container not found.");
        return;
    }

    try {
        loadInteractionToolbarStyles();

        await loadInteractionToolbarDependencies();

        const response = await fetch(
            "/desktop/shared/components/interaction-toolbar/interaction-toolbar.html"
        );

        if (!response.ok) {
            throw new Error("Interaction toolbar HTML could not be loaded.");
        }

        const html = await response.text();

        toolbarContainer.classList.add("interaction-toolbar");
        toolbarContainer.innerHTML = html;

        const switchButton =
            document.getElementById("switchInteractionStyleButton");

        if (!switchButton) {
            console.error("Switch interaction style button not found.");
            return;
        }

        switchButton.addEventListener("click", () => {
            switchInteractionStyle(InteractionStyle.MOBILE);
        });

    } catch (error) {
        console.error("Failed to load interaction toolbar:", error);
    }
}