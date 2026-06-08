/*
 * Shared desktop sidebar component.
 *
 * Responsibilities:
 * - Load sidebar CSS.
 * - Load shared button CSS dependency.
 * - Load sidebar HTML.
 * - Render navigation items.
 * - Show admin navigation only for admin users.
 * - Keep mobile switching visible.
 * - Enable mobile switching only for safe top-level pages.
 * - Delegate interaction-style switching to shared logic.
 * - Trigger shared logout logic.
 *
 * Platform dependencies are loaded by protected-workspace.js.
 */

const SIDEBAR_CSS_ID =
    "desktop-sidebar-css";

const SHARED_BUTTONS_CSS_ID =
    "shared-buttons-css";


function getMobileSwitchEnabledPages() {
    return [
        "dashboard",
        "available-lessons",
        "progress",
        "contact",
        "settings",
        "project-guide"
    ];
}


function getMainNavigationItems() {
    return [
        {
            key: "dashboard",
            label: "Dashboard",
            desktopHref: LLA_PATHS.desktop.protected.welcome,
            requiresAdmin: false
        },
        {
            key: "available-lessons",
            label: "Lesson Library",
            desktopHref: LLA_PATHS.desktop.protected.availableLessons,
            requiresAdmin: false
        },
        {
            key: "progress",
            label: "Progress",
            desktopHref: LLA_PATHS.desktop.protected.progress,
            requiresAdmin: false
        },
        {
            key: "contact",
            label: "Contact Us",
            desktopHref: LLA_PATHS.desktop.protected.contact,
            requiresAdmin: false
        },
        {
            key: "settings",
            label: "Settings",
            desktopHref: LLA_PATHS.desktop.protected.settings,
            requiresAdmin: false
        }
    ];
}


function getSystemNavigationItems() {
    return [
        {
            key: "presentation",
            label: "Presentation",
            desktopHref: LLA_PATHS.desktop.protected.presentation,
            requiresAdmin: false
        },
        {
            key: "admin",
            label: "Admin",
            desktopHref: LLA_PATHS.desktop.protected.admin.dashboard,
            requiresAdmin: true
        },
        {
            key: "project-guide",
            label: "Project Guide",
            desktopHref: LLA_PATHS.desktop.protected.projectGuide,
            requiresAdmin: false
        },
        {
            key: "about",
            label: "About Us",
            desktopHref: LLA_PATHS.desktop.protected.about,
            requiresAdmin: false
        }
    ];
}


function loadCssOnce(cssId, cssPath) {
    if (document.getElementById(cssId)) {
        return;
    }

    const cssLink =
        document.createElement("link");

    cssLink.id =
        cssId;

    cssLink.rel =
        "stylesheet";

    cssLink.href =
        cssPath;

    document.head.appendChild(cssLink);
}


function loadSidebarStyles() {
    loadCssOnce(
        SHARED_BUTTONS_CSS_ID,
        "/desktop/shared/styles/shared-buttons.css"
    );

    loadCssOnce(
        SIDEBAR_CSS_ID,
        "/desktop/protected/shared/components/sidebar/sidebar.css"
    );
}


function isAdminUser(user) {
    return Boolean(
        user &&
        user.isAdmin
    );
}


function isMobileSwitchEnabledPage(activePage) {
    return getMobileSwitchEnabledPages()
        .includes(activePage);
}


function shouldRenderNavigationItem(item, user) {
    if (!item.requiresAdmin) {
        return true;
    }

    return isAdminUser(user);
}


function buildNavigation(items, activePage, user) {
    return items
        .filter((item) =>
            shouldRenderNavigationItem(
                item,
                user
            )
        )
        .map((item) => {
            const activeClass =
                item.key === activePage
                    ? "active"
                    : "";

            return `
                <a class="shared-button sidebar-action-button ${activeClass}" href="${item.desktopHref}">
                    ${item.label}
                </a>
            `;
        })
        .join("");
}


function disableMobileSwitchButton(switchButton) {
    switchButton.disabled =
        true;

    switchButton.title =
        "Mobile view is not available for this page.";
}


function enableMobileSwitchButton(switchButton) {
    switchButton.disabled =
        false;

    switchButton.title =
        "Switch to mobile view.";

    switchButton.addEventListener(
        "click",
        () => {
            switchInteractionStyle(
                InteractionStyle.MOBILE
            );
        }
    );
}


async function loadSidebar(activePage) {
    const sidebarContainer =
        document.getElementById(
            "desktop-sidebar-container"
        );

    if (!sidebarContainer) {
        console.error(
            "Sidebar container not found."
        );

        return;
    }

    try {
        const authenticatedUser =
            requireAuthentication();

        loadSidebarStyles();

        const response =
            await fetch(
                "/desktop/protected/shared/components/sidebar/sidebar.html"
            );

        if (!response.ok) {
            throw new Error(
                "Sidebar HTML could not be loaded."
            );
        }

        const html =
            await response.text();

        sidebarContainer.innerHTML =
            html;

        const mainMenu =
            document.getElementById(
                "sidebar-menu"
            );

        const secondaryMenu =
            document.getElementById(
                "sidebar-secondary-menu"
            );

        if (!mainMenu || !secondaryMenu) {
            console.error(
                "Sidebar menu not found."
            );

            return;
        }

        mainMenu.innerHTML =
            buildNavigation(
                getMainNavigationItems(),
                activePage,
                authenticatedUser
            );

        secondaryMenu.innerHTML =
            buildNavigation(
                getSystemNavigationItems(),
                activePage,
                authenticatedUser
            );

        setupSidebarEvents(
            activePage
        );

    } catch (error) {
        console.error(
            "Failed to load sidebar:",
            error
        );
    }
}


function setupSidebarEvents(activePage) {
    const switchButton =
        document.getElementById(
            "switchToMobileBtn"
        );

    const logoutButton =
        document.getElementById(
            "logoutBtn"
        );

    if (switchButton) {
        if (
            isMobileSwitchEnabledPage(
                activePage
            )
        ) {
            enableMobileSwitchButton(
                switchButton
            );
        } else {
            disableMobileSwitchButton(
                switchButton
            );
        }
    }

    if (!logoutButton) {
        console.error(
            "Logout button not found."
        );

        return;
    }

    logoutButton.addEventListener(
        "click",
        () => {
            logoutUser();
        }
    );
}