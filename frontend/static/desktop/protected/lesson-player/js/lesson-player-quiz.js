/*
 * Lesson player quiz helper.
 *
 * Responsibility:
 * - Manage lesson quiz flow.
 * - Use real lesson quiz questions loaded from the backend.
 * - Track quiz score.
 * - Handle quiz answers.
 */

const LessonPlayerQuiz = (() => {

    const ids = LessonPlayerConstants.elementIds;
    const messages = LessonPlayerConstants.messages;


    function hasQuizQuestions() {
        return (
            Array.isArray(LessonPlayerState.quizQuestions) &&
            LessonPlayerState.quizQuestions.length > 0
        );
    }


    function hasValidOptions(question) {
        return (
            question &&
            Array.isArray(question.options) &&
            question.options.length > 0
        );
    }


    function hasEnoughQuizContent() {
        return (
            hasQuizQuestions() &&
            LessonPlayerState.quizQuestions.every(hasValidOptions)
        );
    }


    function handleQuizUnavailable(onQuizUnavailable) {

        if (typeof onQuizUnavailable === "function") {
            onQuizUnavailable(
                messages.lessonCompletedWithoutQuiz
            );
        }
    }


    function getCurrentQuestion() {
        return LessonPlayerState.quizQuestions[
            LessonPlayerState.currentQuizQuestionIndex
        ];
    }


    function setQuizFeedback(message, status) {
        const feedbackElement =
            document.getElementById(
                ids.quizFeedbackText
            );

        if (!feedbackElement) {
            return;
        }

        feedbackElement.classList.remove(
            "visible",
            "correct",
            "incorrect",
            "warning"
        );

        feedbackElement.textContent =
            message || "";

        if (!message) {
            return;
        }

        feedbackElement.classList.add(
            "visible"
        );

        if (status) {
            feedbackElement.classList.add(
                status
            );
        }
    }


    function findSelectedOption(
        currentQuestion,
        selectedOptionId
    ) {
        return currentQuestion.options.find((option) =>
            String(option.optionId) === String(selectedOptionId)
        );
    }


    function findCorrectOption(currentQuestion) {
        return currentQuestion.options.find((option) =>
            option.isCorrect
        );
    }


    function startQuiz(onQuizUnavailable) {

        if (!hasEnoughQuizContent()) {
            handleQuizUnavailable(
                onQuizUnavailable
            );

            return;
        }

        LessonPlayerState.isQuizActive = true;
        LessonPlayerState.isQuizComplete = false;
        LessonPlayerState.currentQuizQuestionIndex = 0;
        LessonPlayerState.quizScore = 0;

        LessonPlayerRenderer.renderQuizQuestion();
    }


    function submitAnswer() {

        const selectedAnswer =
            document.querySelector(
                'input[name="quizAnswer"]:checked'
            );

        if (!selectedAnswer) {

            setQuizFeedback(
                messages.chooseQuizAnswer,
                "warning"
            );

            return;
        }

        const currentQuestion =
            getCurrentQuestion();

        const selectedOption =
            findSelectedOption(
                currentQuestion,
                selectedAnswer.value
            );

        if (!selectedOption) {
            setQuizFeedback(
                messages.chooseQuizAnswer,
                "warning"
            );

            return;
        }

        const isCorrect = selectedOption.isCorrect;

        if (isCorrect) {

            LessonPlayerState.quizScore += 1;

            setQuizFeedback(
                messages.correctQuizAnswer,
                "correct"
            );
            LessonPlayerRenderer.updateQuizScore();
        } else {

            const correctOption =
                findCorrectOption(currentQuestion);

            setQuizFeedback(
                `${messages.incorrectQuizAnswer} ${correctOption?.optionText || ""}`,
                "incorrect"
            );
        }

        const submitButton =
            document.getElementById(
                ids.submitQuizAnswerButton
            );

        const nextButton =
            document.getElementById(
                ids.nextQuizQuestionButton
            );

        if (submitButton) {
            submitButton.disabled = true;
        }

        if (nextButton) {
            nextButton.disabled = false;
        }
    }


    function goToPreviousQuestion() {

        if (
            LessonPlayerState.currentQuizQuestionIndex <= 0
        ) {
            return;
        }

        LessonPlayerState.currentQuizQuestionIndex -= 1;

        LessonPlayerRenderer.renderQuizQuestion();
    }


    async function goToNextQuestion() {

        const isLastQuestion =
            LessonPlayerState.currentQuizQuestionIndex >=
            LessonPlayerState.quizQuestions.length - 1;

        if (isLastQuestion) {

            LessonPlayerState.isQuizComplete = true;

            await LessonPlayerNavigation.completeLesson(
                messages.lessonCompletedWithQuiz
            );

            return;
        }

        LessonPlayerState.currentQuizQuestionIndex += 1;

        LessonPlayerRenderer.renderQuizQuestion();
    }


    return {
        startQuiz,
        submitAnswer,
        goToPreviousQuestion,
        goToNextQuestion,
        getCurrentQuestion
    };


})();