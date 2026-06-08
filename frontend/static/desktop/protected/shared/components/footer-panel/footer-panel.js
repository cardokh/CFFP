const FOOTER_PANEL_CSS_ID =
    "footer-panel-css";


function loadFooterPanelStyles() {
    if (
        document.getElementById(
            FOOTER_PANEL_CSS_ID
        )
    ) {
        return;
    }

    const cssLink =
        document.createElement("link");

    cssLink.id =
        FOOTER_PANEL_CSS_ID;

    cssLink.rel =
        "stylesheet";

    cssLink.href =
        "/desktop/protected/shared/components/footer-panel/footer-panel.css";

    document.head.appendChild(cssLink);
}


async function loadFooterPanel() {

    const container =
        document.getElementById(
            "footer-panel-container"
        );

    if (!container) {
        console.error(
            "Footer panel container not found."
        );

        return;
    }

    try {
        loadFooterPanelStyles();

        const response =
            await fetch(
                "/desktop/protected/shared/components/footer-panel/footer-panel.html"
            );

        if (!response.ok) {
            throw new Error(
                "Footer panel HTML could not be loaded."
            );
        }

        const html =
            await response.text();

        container.innerHTML =
            html;

    } catch (error) {
        console.error(
            "Failed to load footer panel:",
            error
        );
    }
}