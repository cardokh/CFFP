/*
 * Mobile start lesson preview controller.
 *
 * Responsibility:
 * - Load and display a lightweight lesson preview.
 * - Provide navigation to the mobile lesson player.
 */

const LESSON_TITLE_ID =
    "lessonTitle";

const LESSON_DESCRIPTION_ID =
    "lessonDescription";

const LEARNING_ITEM_COUNT_ID =
    "learningItemCount";

const START_LESSON_PLAYER_BUTTON_ID =
    "startLessonPlayerButton";

const BACK_TO_LESSON_DETAILS_BUTTON_ID =
    "backToLessonDetailsButton";


function getLessonIdFromUrl() {

    const params =
        new URLSearchParams(
            window.location.search
        );

    return Number(
        params.get("lessonId")
    );
}


function getAuthenticatedUserId() {

    const authenticatedUser =
        requireAuthentication();

    if (
        !authenticatedUser ||
        !authenticatedUser.userId
    ) {
        throw new Error(
            "Authenticated user ID is missing."
        );
    }

    return authenticatedUser.userId;
}


async function markLessonInProgress(
    userId,
    lessonId
) {

    const response =
        await postJson(
            LLA_API_ENDPOINTS
                .admin
                .userLessons
                .markInProgress(userId),

            {
                lesson_id: lessonId
            }
        );

    if (!response.success) {

        throw new Error(
            response.error ||
            "Failed to update lesson status."
        );
    }
}


function navigateToLessonPlayer() {

    const lessonId =
        getLessonIdFromUrl();

    if (!lessonId) {
        return;
    }

    window.location.href =
        `/mobile/protected/lesson-player.html?lessonId=${lessonId}`;
}


function navigateBackToLessonDetails() {

    const lessonId =
        getLessonIdFromUrl();

    if (!lessonId) {

        window.location.href =
            window.LLA_PATHS.mobile.protected.availableLessons;

        return;
    }

    window.location.href =
        `/mobile/protected/student-lesson-details.html?lessonId=${lessonId}`;
}


function renderLessonPreview(
    lesson,
    learningItems
) {

    document.getElementById(
        LESSON_TITLE_ID
    ).textContent =
        lesson.title ||
        "Untitled lesson";

    document.getElementById(
        LESSON_DESCRIPTION_ID
    ).textContent =
        lesson.description ||
        "No lesson description available.";

    document.getElementById(
        LEARNING_ITEM_COUNT_ID
    ).textContent =
        String(
            learningItems.length
        );
}


function renderError(message) {

    document.getElementById(
        LESSON_TITLE_ID
    ).textContent =
        "Could not load lesson";

    document.getElementById(
        LESSON_DESCRIPTION_ID
    ).textContent =
        message ||
        "Failed to load lesson preview.";

    document.getElementById(
        LEARNING_ITEM_COUNT_ID
    ).textContent =
        "-";
}


function setupStartLessonActions() {

    const startLessonPlayerButton =
        document.getElementById(
            START_LESSON_PLAYER_BUTTON_ID
        );

    const backToLessonDetailsButton =
        document.getElementById(
            BACK_TO_LESSON_DETAILS_BUTTON_ID
        );

    if (startLessonPlayerButton) {
        startLessonPlayerButton.addEventListener(
            "click",
            navigateToLessonPlayer
        );
    }

    if (backToLessonDetailsButton) {
        backToLessonDetailsButton.addEventListener(
            "click",
            navigateBackToLessonDetails
        );
    }
}


async function loadStartLessonPreview() {

    const lessonId =
        getLessonIdFromUrl();

    if (!lessonId) {

        renderError(
            "Lesson ID is missing."
        );

        return;
    }

    try {

        const userId =
            getAuthenticatedUserId();

        await markLessonInProgress(
            userId,
            lessonId
        );

        const lessonData =
            await getJson(
                LLA_API_ENDPOINTS
                    .admin
                    .lessons
                    .byId(lessonId)
            );

        const learningItemsData =
            await getJson(
                LLA_API_ENDPOINTS
                    .admin
                    .lessons
                    .learningItems(lessonId)
            );

        if (
            !lessonData.success ||
            !lessonData.lesson
        ) {
            throw new Error(
                lessonData.error ||
                "Lesson not found."
            );
        }

        renderLessonPreview(
            lessonData.lesson,
            learningItemsData
                .lessonLearningItems || []
        );

    } catch (error) {

        console.error(error);

        renderError(
            error.message
        );
    }
}


setupStartLessonActions();

loadStartLessonPreview();