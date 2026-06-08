/*
 * Protected desktop workspace loader.
 *
 * Responsibilities:
 * - Centralize protected desktop platform loading.
 * - Load shared platform scripts.
 * - Guard protected pages behind authenticated frontend session state.
 * - Load sidebar, header panel, and footer panel from one place.
 * - Keep protected pages from duplicating shell initialization.
 *
 * Architectural rules:
 * - Protected pages should call this loader instead of loading shell panels directly.
 * - Page-specific JavaScript should only initialize page-specific behavior.
 * - Protected page authentication must be handled centrally here.
 */

const PROTECTED_WORKSPACE_PLATFORM_SCRIPT_PATHS = [
    "/shared/frontend-paths.js",
    "/shared/interaction-style.js",
    "/shared/session-manager.js",
    "/shared/api-endpoints.js",
    "/shared/api.js",
    "/shared/ui-state.js",
    "/shared/ui-render.js",
    "/shared/ui-messages.js"
];

const PROTECTED_WORKSPACE_COMPONENT_SCRIPT_PATHS = [
    "/desktop/protected/shared/components/sidebar/sidebar.js",
    "/desktop/protected/shared/components/header-panel/header-panel.js",
    "/desktop/protected/shared/components/footer-panel/footer-panel.js"
];


function loadProtectedWorkspaceScript(scriptPath) {
    return new Promise((resolve, reject) => {
        const existingScript =
            document.querySelector(
                `script[src="${scriptPath}"]`
            );

        if (existingScript) {
            resolve();
            return;
        }

        const script =
            document.createElement("script");

        script.src =
            scriptPath;

        script.onload =
            resolve;

        script.onerror =
            () => reject(
                new Error(
                    `Failed to load protected workspace script: ${scriptPath}`
                )
            );

        document.body.appendChild(script);
    });
}


async function loadProtectedWorkspaceScripts(scriptPaths) {
    for (const scriptPath of scriptPaths) {
        await loadProtectedWorkspaceScript(scriptPath);
    }
}


function requireProtectedWorkspaceAuthentication() {
    if (typeof requireAuthentication !== "function") {
        throw new Error(
            "requireAuthentication is unavailable. Load session-manager.js before requiring authentication."
        );
    }

    const authenticatedUser =
        requireAuthentication();

    if (!authenticatedUser) {
        throw new Error(
            "Protected workspace initialization stopped because no authenticated user was found."
        );
    }

    return authenticatedUser;
}


async function loadProtectedWorkspaceComponents(activeSidebarItem) {
    await Promise.all([
        loadSidebar(activeSidebarItem),
        loadHeaderPanel(),
        loadFooterPanel()
    ]);
}


async function loadProtectedWorkspace(activeSidebarItem) {
    try {
        await loadProtectedWorkspaceScripts(
            PROTECTED_WORKSPACE_PLATFORM_SCRIPT_PATHS
        );

        const authenticatedUser =
            requireProtectedWorkspaceAuthentication();

        await loadProtectedWorkspaceScripts(
            PROTECTED_WORKSPACE_COMPONENT_SCRIPT_PATHS
        );

        await loadProtectedWorkspaceComponents(
            activeSidebarItem
        );

        return authenticatedUser;

    } catch (error) {
        console.error(
            "Failed to load protected workspace:",
            error
        );

        return null;
    }
}