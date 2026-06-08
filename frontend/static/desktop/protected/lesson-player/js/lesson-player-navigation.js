/*
 * Lesson player navigation helper.
 *
 * Responsibility:
 * - Handle lesson-player navigation flow.
 * - Move between learning items.
 * - Complete lessons.
 * - Navigate between lesson-player pages.
 */

const LessonPlayerNavigation = (() => {

    const messages = LessonPlayerConstants.messages;
    const queryParams = LessonPlayerConstants.queryParams;


    function getAuthenticatedUserId() {
        const authenticatedUser =
            requireAuthentication();

        if (
            !authenticatedUser ||
            !authenticatedUser.userId
        ) {
            throw new Error(
                messages.authenticatedUserIdMissing
            );
        }

        return authenticatedUser.userId;
    }


    function goBackToStartLesson() {

        if (LessonPlayerState.isLessonComplete) {
            window.location.href =
                LLA_PATHS.desktop.protected.availableLessons;

            return;
        }

        window.location.href =
            `${LLA_PATHS.desktop.protected.studentLessonDetails}?${queryParams.lessonId}=${LessonPlayerState.currentLessonId}`;
    }


    function getLessonCompletionPayload() {
        const hasQuizQuestions =
            Array.isArray(LessonPlayerState.quizQuestions) &&
            LessonPlayerState.quizQuestions.length > 0;

        return {
            lesson_id:
                LessonPlayerState.currentLessonId,

            score:
                hasQuizQuestions
                    ? LessonPlayerState.quizScore
                    : null,

            total_questions:
                hasQuizQuestions
                    ? LessonPlayerState.quizQuestions.length
                    : null
        };
    }


    async function markLessonCompleted() {
        const userId =
            getAuthenticatedUserId();

        const response =
            await postJson(
                LLA_API_ENDPOINTS.admin.userLessons.markCompleted(
                    userId
                ),
                getLessonCompletionPayload()
            );

        if (!response.success) {
            throw new Error(
                response.error ||
                messages.failedToCompleteLesson
            );
        }
    }


    async function completeLesson(completionMessage) {
        try {
            await markLessonCompleted();

            LessonPlayerState.isLessonComplete = true;

            LessonPlayerRenderer.renderLessonCompleted(
                messages.lessonCompletedTitle,
                completionMessage
            );

        } catch (error) {

            alert(
                error.message ||
                messages.failedToCompleteLesson
            );
        }
    }


    function goToPreviousLearningItem() {

        if (LessonPlayerState.isQuizActive) {
            LessonPlayerQuiz.goToPreviousQuestion();
            return;
        }

        if (
            LessonPlayerState.currentLearningItemIndex <= 0
        ) {
            return;
        }

        LessonPlayerState.currentLearningItemIndex -= 1;

        LessonPlayerRenderer.renderCurrentLearningItem();
    }


    async function goToNextLearningItem() {

        if (LessonPlayerState.isQuizActive) {
            await LessonPlayerQuiz.goToNextQuestion();
            return;
        }

        const isLastItem =
            LessonPlayerState.currentLearningItemIndex >=
            LessonPlayerState.learningItems.length - 1;

        if (isLastItem) {
            LessonPlayerQuiz.startQuiz(
                completeLesson
            );

            return;
        }

        LessonPlayerState.currentLearningItemIndex += 1;

        LessonPlayerRenderer.renderCurrentLearningItem();
    }


    return {
        goBackToStartLesson,
        goToPreviousLearningItem,
        goToNextLearningItem,
        completeLesson
    };

})();