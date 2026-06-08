/*
 * Start lesson preview page controller.
 *
 * Responsibilities:
 * - Read the lesson ID from the URL.
 * - Load lesson metadata and assigned learning items.
 * - Mark the lesson as in progress when the learner enters the start flow.
 * - Render a compact lesson preparation preview.
 * - Navigate to the real lesson player.
 */

const START_LESSON_MESSAGE_ID =
    "startLessonMessage";

const LESSON_TITLE_ID =
    "lessonTitle";

const LESSON_DESCRIPTION_ID =
    "lessonDescription";

const LEARNING_ITEM_COUNT_ID =
    "learningItemCount";


function getLessonIdFromUrl() {
    const params =
        new URLSearchParams(window.location.search);

    return Number(params.get("lessonId"));
}


function getAuthenticatedUserId() {
    const authenticatedUser =
        requireAuthentication();

    if (!authenticatedUser || !authenticatedUser.userId) {
        throw new Error("Authenticated user ID is missing.");
    }

    return authenticatedUser.userId;
}


function navigateBackToLessonLibrary() {
    window.location.href =
        LLA_PATHS.desktop.protected.availableLessons;
}


function navigateToLessonPlayer(lessonId) {
    window.location.href =
        `${LLA_PATHS.desktop.protected.lessonPlayer}?lessonId=${lessonId}`;
}


async function markLessonInProgress(userId, lessonId) {
    const response =
        await postJson(
            LLA_API_ENDPOINTS.admin.userLessons.markInProgress(userId),
            {
                lesson_id: lessonId
            }
        );

    if (!response.success) {
        throw new Error(
            response.error || "Failed to update lesson status."
        );
    }
}


function renderLessonPreview(lesson, learningItems) {
    document.getElementById(LESSON_TITLE_ID).textContent =
        lesson.title || "Untitled lesson";

    document.getElementById(LESSON_DESCRIPTION_ID).textContent =
        lesson.description || "No lesson description available.";

    document.getElementById(LEARNING_ITEM_COUNT_ID).textContent =
        String(learningItems.length);
}


async function loadStartLessonPreview() {
    const lessonId =
        getLessonIdFromUrl();

    if (!lessonId) {
        document.getElementById(LESSON_TITLE_ID).textContent =
            "Lesson ID is missing.";

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
                LLA_API_ENDPOINTS.admin.lessons.byId(lessonId)
            );

        const learningItemsData =
            await getJson(
                LLA_API_ENDPOINTS.admin.lessons.learningItems(lessonId)
            );

        if (!lessonData.success || !lessonData.lesson) {
            throw new Error(
                lessonData.error || "Lesson not found."
            );
        }

        renderLessonPreview(
            lessonData.lesson,
            learningItemsData.lessonLearningItems || []
        );

        document
            .getElementById("continueToLessonPlayerButton")
            .addEventListener("click", () => {
                navigateToLessonPlayer(lessonId);
            });

    } catch (error) {
        console.error(error);

        document.getElementById(LESSON_TITLE_ID).textContent =
            "Could not load lesson.";

        document.getElementById(LESSON_DESCRIPTION_ID).textContent =
            error.message || "Failed to load lesson preview.";
    }
}


document
    .getElementById("backToMyLessonsButton")
    .addEventListener(
        "click",
        navigateBackToLessonLibrary
    );


loadStartLessonPreview();