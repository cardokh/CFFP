/*
 * Lesson player header component.
 *
 * Responsibility:
 * - Load the lesson-player-specific header HTML.
 * - Keep lesson-player header behavior isolated from the lesson-player page.
 */

const LessonPlayerHeader = (() => {

    const HEADER_CONTAINER_ID =
        "header-panel-container";

    const HEADER_HTML_PATH =
        "./lesson-player-header/lesson-player-header.html";


    async function loadHeaderMarkup() {
        const container =
            document.getElementById(
                HEADER_CONTAINER_ID
            );

        if (!container) {
            return;
        }

        const response =
            await fetch(
                HEADER_HTML_PATH
            );

        if (!response.ok) {
            throw new Error(
                "Failed to load lesson player header."
            );
        }

        container.innerHTML =
            await response.text();
    }


    async function init() {
        await loadHeaderMarkup();
    }


    return {
        init
    };

})();


LessonPlayerHeader.init();