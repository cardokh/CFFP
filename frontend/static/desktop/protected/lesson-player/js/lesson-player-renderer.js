/*
 * Lesson player renderer.
 *
 * Responsibility:
 * - Render lesson-player state into the DOM.
 * - Update UI text and button states.
 * - Keep rendering logic isolated from the controller.
 */

const LessonPlayerRenderer = (() => {

    const ids = LessonPlayerConstants.elementIds;
    const labels = LessonPlayerConstants.labels;
    const fallback = LessonPlayerConstants.fallback;


    function getDisplayValue(value) {
        return value || fallback.emptyText;
    }


    function getCurrentLearningItem() {
        return LessonPlayerState.learningItems[
            LessonPlayerState.currentLearningItemIndex
        ];
    }


    function setText(elementId, value) {
        const element =
            document.getElementById(elementId);

        if (element) {
            element.textContent =
                getDisplayValue(value);
        }
    }


    function setButtonDisabled(buttonId, disabled) {
        const button =
            document.getElementById(buttonId);

        if (button) {
            button.disabled = disabled;
        }
    }


    function setButtonText(buttonId, text) {
        const button =
            document.getElementById(buttonId);

        if (button) {
            button.textContent =
                text;
        }
    }


    function setProgressionButtonState(buttonId, isProgressionAction) {
        const button =
            document.getElementById(buttonId);

        if (!button) {
            return;
        }

        button.classList.toggle(
            "lesson-player-progression-button",
            isProgressionAction
        );
    }


    function setPanelVisible(panelName, visible) {
        const panel =
            document.querySelector(
                `[data-lesson-player-panel="${panelName}"]`
            );

        if (!panel) {
            return;
        }

        panel.classList.toggle(
            "hidden",
            !visible
        );
    }


    function setElementVisible(elementId, visible) {
        const element =
            document.getElementById(elementId);

        if (!element) {
            return;
        }

        element.classList.toggle(
            "hidden",
            !visible
        );
    }


    function clearQuizFeedback() {
        const feedbackElement =
            document.getElementById(
                ids.quizFeedbackText
            );

        if (!feedbackElement) {
            return;
        }

        feedbackElement.textContent = "";

        feedbackElement.classList.remove(
            "visible",
            "correct",
            "incorrect",
            "warning"
        );
    }


    function setLessonPlayerLegend() {
        const legendElement =
            document.getElementById(
                "lessonPlayerCardLegend"
            );

        if (!legendElement) {
            return;
        }

        const lessonTitle =
            LessonPlayerState.currentLesson?.title ||
            fallback.lessonTitle;

        legendElement.textContent =
            `Current lesson — ${lessonTitle}`;
    }


    function setMessage(title, message) {
        setText(ids.lessonPlayerTitle, title);
        setText(ids.sourceText, message);
    }


    function showLearningMode() {
        setPanelVisible("learning-item-panel", true);
        setPanelVisible("practice-panel", true);
        setPanelVisible("pronunciation-options-panel", true);
        setElementVisible(ids.previousLearningItemButton, true);
        setElementVisible(ids.nextLearningItemButton, true);
        setElementVisible(ids.favoriteLearningItemButton, true);
        setElementVisible(ids.knowLearningItemButton, true);
        setElementVisible(ids.needsPracticeLearningItemButton, true);

        setPanelVisible("quiz-panel", false);
        setElementVisible(ids.submitQuizAnswerButton, false);
        setElementVisible(ids.nextQuizQuestionButton, false);
        setElementVisible(ids.lessonPlayerProgressText, true);

        setProgressionButtonState(
            ids.submitQuizAnswerButton,
            false
        );

        setProgressionButtonState(
            ids.nextQuizQuestionButton,
            false
        );

        setButtonText(
            ids.previousLearningItemButton,
            "Previous"
        );
    }


    function showQuizMode() {
        setPanelVisible("quiz-panel", true);
        setElementVisible(ids.submitQuizAnswerButton, true);
        setElementVisible(ids.nextQuizQuestionButton, true);
        setElementVisible(ids.lessonPlayerProgressText, true);

        setPanelVisible("learning-item-panel", false);
        setPanelVisible("practice-panel", false);
        setPanelVisible("pronunciation-options-panel", false);
        setElementVisible(ids.previousLearningItemButton, false);
        setElementVisible(ids.nextLearningItemButton, false);
        setElementVisible(ids.favoriteLearningItemButton, false);
        setElementVisible(ids.knowLearningItemButton, false);
        setElementVisible(ids.needsPracticeLearningItemButton, false);

        setProgressionButtonState(
            ids.nextLearningItemButton,
            false
        );

        setProgressionButtonState(
            ids.submitQuizAnswerButton,
            true
        );

        setProgressionButtonState(
            ids.nextQuizQuestionButton,
            true
        );
    }


    function renderLessonCompleted(title, message) {
        setPanelVisible("learning-item-panel", false);
        setPanelVisible("practice-panel", false);
        setPanelVisible("quiz-panel", false);
        setPanelVisible("pronunciation-options-panel", false);

        setPanelVisible("lesson-completed-panel", true);

        setText(
            ids.lessonCompletedTitle,
            title
        );

        setText(
            ids.lessonCompletedMessage,
            message
        );

        setText(
            "lessonCompletedLessonTitle",
            LessonPlayerState.currentLesson?.title || "Lesson"
        );

        setText(
            "lessonCompletedQuizResult",
            `Quiz result: ${LessonPlayerState.quizScore} / ${LessonPlayerState.quizQuestions.length}`
        );

        setElementVisible(
            ids.previousLearningItemButton,
            false
        );

        setElementVisible(
            ids.nextLearningItemButton,
            false
        );

        setElementVisible(
            ids.favoriteLearningItemButton,
            false
        );

        setElementVisible(
            ids.knowLearningItemButton,
            false
        );

        setElementVisible(
            ids.needsPracticeLearningItemButton,
            false
        );

        setElementVisible(
            ids.submitQuizAnswerButton,
            false
        );

        setElementVisible(
            ids.nextQuizQuestionButton,
            false
        );

        setElementVisible(
            ids.lessonPlayerProgressText,
            false
        );

        setProgressionButtonState(
            ids.nextLearningItemButton,
            false
        );

        setProgressionButtonState(
            ids.submitQuizAnswerButton,
            false
        );

        setProgressionButtonState(
            ids.nextQuizQuestionButton,
            false
        );

        setText(
            ids.lessonPlayerProgressText,
            "Lesson completed"
        );

        setButtonText(
            ids.backToStartLessonButton,
            "Back to Lesson Library"
        );
    }


    function renderAiExamplesRoadmapCard() {
        setText(
            ids.thirdExampleText,
            ""
        );

        setText(
            ids.thirdExampleTranslationText,
            ""
        );

        const aiExamplesButton =
            document.getElementById(
                ids.moreExamplesButton
            );

        if (aiExamplesButton) {
            aiExamplesButton.textContent =
                labels.moreExamples;

            aiExamplesButton.disabled =
                true;
        }
    }


    function renderGeneratedExamples() {
        const secondGeneratedExample =
            LessonPlayerExamples.getGeneratedExample(1) ||
            LessonPlayerExamples.getGeneratedExample(0);

        setText(
            ids.secondExampleText,
            secondGeneratedExample?.sourceText
        );

        renderAiExamplesRoadmapCard();
    }


    function renderFallbackExamples() {
        setText(
            ids.secondExampleText,
            "Click the microphone and say something."
        );

        renderAiExamplesRoadmapCard();
    }


    function hasQuizQuestions() {
        return (
            Array.isArray(LessonPlayerState.quizQuestions) &&
            LessonPlayerState.quizQuestions.length > 0
        );
    }


    function updateNavigationButtons() {
        const currentLearningItem =
            getCurrentLearningItem();

        setButtonDisabled(
            ids.previousLearningItemButton,
            LessonPlayerState.currentLearningItemIndex === 0
        );

        setButtonDisabled(
            ids.moreExamplesButton,
            true
        );

        setButtonDisabled(
            ids.playSoundButton,
            !currentLearningItem ||
            !currentLearningItem.sourceText
        );

        setButtonDisabled(
            ids.playEnglishSoundButton,
            !currentLearningItem ||
            !currentLearningItem.englishTranslation
        );

        setButtonDisabled(
            ids.playExampleSoundButton,
            !currentLearningItem ||
            !currentLearningItem.exampleText
        );

        const nextButton =
            document.getElementById(
                ids.nextLearningItemButton
            );

        if (nextButton) {
            const isLastLearningItem =
                LessonPlayerState.currentLearningItemIndex ===
                LessonPlayerState.learningItems.length - 1;

            const nextButtonText =
                isLastLearningItem && hasQuizQuestions()
                    ? labels.startQuiz
                    : isLastLearningItem
                        ? labels.finishLesson
                        : labels.next;

            nextButton.disabled = false;

            nextButton.textContent =
                nextButtonText;

            setProgressionButtonState(
                ids.nextLearningItemButton,
                true
            );
        }
    }


    function renderCurrentLearningItem() {
        if (LessonPlayerState.learningItems.length === 0) {
            return;
        }

        LessonPlayerState.generatedExamples = [];

        LessonPlayerState.isQuizActive = false;
        LessonPlayerState.isQuizComplete = false;

        showLearningMode();

        const learningItem =
            getCurrentLearningItem();

        setLessonPlayerLegend();

        setText(
            ids.lessonPlayerProgressText,
            `Item ${LessonPlayerState.currentLearningItemIndex + 1} of ${LessonPlayerState.learningItems.length}`
        );

        setText(ids.sourceText, learningItem.sourceText);
        setText(ids.englishTranslation, learningItem.englishTranslation);
        setText(ids.pronunciationText, learningItem.pronunciation);

        setText(ids.exampleText, learningItem.exampleText);

        renderFallbackExamples(learningItem);

        updateNavigationButtons();

        LessonPlayerProgress.updateButtons();
    }


    function updateQuizScore() {
        setText(
            ids.quizScoreText,
            `Score: ${LessonPlayerState.quizScore} / ${LessonPlayerState.quizQuestions.length}`
        );
    }


    function renderQuizQuestion() {
        const currentQuestion =
            LessonPlayerQuiz.getCurrentQuestion();

        if (!currentQuestion) {
            return;
        }

        showQuizMode();

        setLessonPlayerLegend();

        setText(
            ids.lessonPlayerProgressText,
            `Question ${LessonPlayerState.currentQuizQuestionIndex + 1} of ${LessonPlayerState.quizQuestions.length}`
        );

        setText(
            ids.quizQuestionText,
            currentQuestion.questionText
        );

        clearQuizFeedback();

        setText(
            ids.quizScoreText,
            `Score: ${LessonPlayerState.quizScore} / ${LessonPlayerState.quizQuestions.length}`
        );

        const answerContainer =
            document.getElementById(
                ids.quizAnswerOptions
            );

        if (answerContainer) {
            answerContainer.innerHTML = "";

            currentQuestion.options.forEach((option) => {
                const optionLabel =
                    document.createElement("label");

                optionLabel.className =
                    "lesson-quiz-option";

                const input =
                    document.createElement("input");

                input.type = "radio";
                input.name = "quizAnswer";
                input.value = option.optionId;

                const optionText =
                    document.createElement("span");

                optionText.textContent =
                    option.optionText;

                optionLabel.appendChild(input);
                optionLabel.appendChild(optionText);

                answerContainer.appendChild(optionLabel);
            });
        }

        setButtonDisabled(
            ids.previousLearningItemButton,
            LessonPlayerState.currentQuizQuestionIndex === 0
        );

        const submitButton =
            document.getElementById(
                ids.submitQuizAnswerButton
            );

        const nextQuizButton =
            document.getElementById(
                ids.nextQuizQuestionButton
            );

        if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent =
                labels.submitAnswer;

            setProgressionButtonState(
                ids.submitQuizAnswerButton,
                true
            );
        }

        if (nextQuizButton) {
            const nextQuizButtonText =
                LessonPlayerState.currentQuizQuestionIndex >=
                    LessonPlayerState.quizQuestions.length - 1
                    ? labels.finishQuiz
                    : labels.nextQuestion;

            nextQuizButton.disabled = true;

            nextQuizButton.textContent =
                nextQuizButtonText;

            setProgressionButtonState(
                ids.nextQuizQuestionButton,
                true
            );
        }
    }


    return {
        setMessage,
        renderCurrentLearningItem,
        renderGeneratedExamples,
        renderQuizQuestion,
        renderLessonCompleted,
        updateNavigationButtons,
        updateQuizScore
    };
})();