/*
 * Shared mobile top panel component.
 *
 * Responsibilities:
 * - Load top panel CSS.
 * - Load top panel HTML.
 * - Handle protected mobile top navigation.
 */

const MOBILE_TOP_PANEL_CSS_ID =
    "mobile-top-panel-css";

function loadMobileTopPanelStyles() {
    if (document.getElementById(MOBILE_TOP_PANEL_CSS_ID)) {
        return;
    }

    const cssLink =
        document.createElement("link");

    cssLink.id =
        MOBILE_TOP_PANEL_CSS_ID;

    cssLink.rel =
        "stylesheet";

    cssLink.href =
        "../shared/components/top-panel/top-panel.css";

    document.head.appendChild(cssLink);
}

async function loadMobileTopPanel(activePage) {
    const container =
        document.getElementById(
            "mobile-top-panel-container"
        );

    if (!container) {
        console.error(
            "Mobile top panel container not found."
        );

        return;
    }

    try {
        loadMobileTopPanelStyles();

        const response =
            await fetch(
                "../shared/components/top-panel/top-panel.html"
            );

        if (!response.ok) {
            throw new Error(
                "Mobile top panel HTML could not be loaded."
            );
        }

        const html =
            await response.text();

        container.innerHTML =
            html;

        setupMobileTopPanelEvents(activePage);

    } catch (error) {
        console.error(
            "Failed to load mobile top panel:",
            error
        );
    }
}

function setMobileTopPanelActiveState(activePage) {
    const activeMap = {
        "lesson-library": "mobileLessonLibraryButton",
        progress: "mobileProgressButton",
        "project-guide": "mobileProjectGuideButton",
        contact: "mobileContactButton"
    };

    const activeButtonId =
        activeMap[activePage];

    if (!activeButtonId) {
        return;
    }

    const activeButton =
        document.getElementById(activeButtonId);

    if (activeButton) {
        activeButton.classList.add("active");
    }
}

function setupMobileTopPanelEvents(activePage) {
    const lessonLibraryButton =
        document.getElementById(
            "mobileLessonLibraryButton"
        );

    const progressButton =
        document.getElementById(
            "mobileProgressButton"
        );

    const projectGuideButton =
        document.getElementById(
            "mobileProjectGuideButton"
        );

    const contactButton =
        document.getElementById(
            "mobileContactButton"
        );

    if (lessonLibraryButton) {
        lessonLibraryButton.addEventListener("click", () => {
            window.location.href =
                window.LLA_PATHS.mobile.protected.availableLessons;
        });
    }

    if (progressButton) {
        progressButton.addEventListener("click", () => {
            window.location.href =
                window.LLA_PATHS.mobile.protected.progress;
        });
    }

    if (projectGuideButton) {
        projectGuideButton.addEventListener("click", () => {
            window.location.href =
                window.LLA_PATHS.mobile.protected.projectGuide;
        });
    }

    if (contactButton) {
        contactButton.addEventListener("click", () => {
            window.location.href =
                window.LLA_PATHS.mobile.protected.contact;
        });
    }

    setMobileTopPanelActiveState(activePage);
}