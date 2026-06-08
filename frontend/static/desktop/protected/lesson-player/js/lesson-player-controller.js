/*
 * Lesson player controller.
 *
 * Responsibility:
 * - Initialize the lesson-player page.
 * - Wire UI events.
 * - Load lesson data.
 * - Coordinate feature modules.
 */

const LessonPlayerController = (() => {

    const ids = LessonPlayerConstants.elementIds;
    const labels = LessonPlayerConstants.labels;
    const messages = LessonPlayerConstants.messages;
    const queryParams = LessonPlayerConstants.queryParams;


    function getLessonIdFromUrl() {
        const params =
            new URLSearchParams(window.location.search);

        return Number(
            params.get(queryParams.lessonId)
        );
    }


    function getCurrentLearningItem() {
        return LessonPlayerState.learningItems[
            LessonPlayerState.currentLearningItemIndex
        ];
    }


    function getTextFromElement(elementId) {
        const element =
            document.getElementById(elementId);

        return element?.textContent || "";
    }


    function addClickHandler(buttonId, handler) {
        const button =
            document.getElementById(buttonId);

        if (button) {
            button.addEventListener(
                "click",
                handler
            );
        }
    }


    function updatePronunciationButtonStates(
        activeButtonId,
        buttonIds
    ) {

        buttonIds.forEach((buttonId) => {

            const button =
                document.getElementById(buttonId);

            if (!button) {
                return;
            }

            button.classList.remove(
                "primary"
            );

            button.classList.add(
                "secondary"
            );
        });

        const activeButton =
            document.getElementById(
                activeButtonId
            );

        if (!activeButton) {
            return;
        }

        activeButton.classList.remove(
            "secondary"
        );

        activeButton.classList.add(
            "primary"
        );
    }


    function setNeutralTone() {

        LessonPlayerSpeech.setTone(
            "neutral"
        );

        updatePronunciationButtonStates(
            "toneNeutralButton",
            [
                "toneNeutralButton",
                "toneEncouragingButton"
            ]
        );
    }


    function setEncouragingTone() {

        LessonPlayerSpeech.setTone(
            "encouraging"
        );

        updatePronunciationButtonStates(
            "toneEncouragingButton",
            [
                "toneNeutralButton",
                "toneEncouragingButton"
            ]
        );
    }


    function setSlowSpeed() {

        LessonPlayerSpeech.setSpeed(
            "slow"
        );

        updatePronunciationButtonStates(
            "speedSlowButton",
            [
                "speedSlowButton",
                "speedNormalButton",
                "speedFastButton"
            ]
        );
    }


    function setNormalSpeed() {

        LessonPlayerSpeech.setSpeed(
            "normal"
        );

        updatePronunciationButtonStates(
            "speedNormalButton",
            [
                "speedSlowButton",
                "speedNormalButton",
                "speedFastButton"
            ]
        );
    }


    function setFastSpeed() {

        LessonPlayerSpeech.setSpeed(
            "fast"
        );

        updatePronunciationButtonStates(
            "speedFastButton",
            [
                "speedSlowButton",
                "speedNormalButton",
                "speedFastButton"
            ]
        );
    }


    function playCurrentSourceText() {
        const learningItem =
            getCurrentLearningItem();

        LessonPlayerSpeech.speakSwedish(
            learningItem?.sourceText
        );
    }


    function practiceCurrentPronunciation() {
        const learningItem =
            getCurrentLearningItem();

        LessonPlayerProgress.markPronunciationPracticed();

        LessonPlayerSpeech.speakSwedishPractice(
            learningItem?.sourceText
        );
    }


    function playCurrentEnglishTranslation() {
        const learningItem =
            getCurrentLearningItem();

        LessonPlayerSpeech.speakEnglish(
            learningItem?.englishTranslation
        );
    }


    function playCurrentExampleText() {
        const learningItem =
            getCurrentLearningItem();

        LessonPlayerSpeech.speakSwedish(
            learningItem?.exampleText
        );
    }


    function playSecondExampleText() {
        LessonPlayerSpeech.speakSwedish(
            getTextFromElement(
                ids.secondExampleText
            )
        );
    }


    function startSpeechRecognition() {

        const resultElement =
            document.getElementById(
                "speechRecognitionResultText"
            );

        LessonPlayerSpeech.recognizeSwedishSpeech(

            (transcript) => {

                const speechTextElement =
                    document.getElementById(
                        ids.secondExampleText
                    );

                if (speechTextElement) {
                    speechTextElement.textContent =
                        transcript;
                }

                if (resultElement) {
                    resultElement.textContent = "";
                }

                LessonPlayerSpeech.speakSwedish(
                    transcript
                );
            },
            (errorMessage) => {

                const speechTextElement =
                    document.getElementById(
                        ids.secondExampleText
                    );

                if (speechTextElement) {
                    speechTextElement.textContent =
                        "Click the microphone and say something.";
                }

                if (resultElement) {
                    resultElement.textContent =
                        `You said: ${errorMessage}`;
                }
            },

            () => {

                if (resultElement) {
                    resultElement.textContent =
                        "Listening...";
                }
            }
        );
    }


    function playThirdExampleText() {
        LessonPlayerSpeech.speakSwedish(
            getTextFromElement(
                ids.thirdExampleText
            )
        );
    }


    async function handleMoreExamples() {
        const moreExamplesButton =
            document.getElementById(
                ids.moreExamplesButton
            );

        try {

            if (moreExamplesButton) {
                moreExamplesButton.disabled = true;
                moreExamplesButton.textContent =
                    labels.loading;
            }

            await LessonPlayerExamples.loadGeneratedExamples();

            LessonPlayerRenderer.renderGeneratedExamples();

        } catch (error) {

            alert(
                error.message ||
                messages.couldNotLoadMoreExamples
            );

        } finally {

            if (moreExamplesButton) {
                moreExamplesButton.disabled = false;
                moreExamplesButton.textContent =
                    labels.moreExamples;
            }
        }
    }


    async function loadLessonPlayer() {
        LessonPlayerState.currentLessonId =
            getLessonIdFromUrl();

        if (!LessonPlayerState.currentLessonId) {

            LessonPlayerRenderer.setMessage(
                messages.lessonIdMissingTitle,
                messages.lessonIdMissingBody
            );

            return;
        }

        try {

            const lessonResponse =
                await getJson(
                    LLA_API_ENDPOINTS.admin.lessons.byId(
                        LessonPlayerState.currentLessonId
                    )
                );

            const learningItemsResponse =
                await getJson(
                    LLA_API_ENDPOINTS.admin.lessons.learningItems(
                        LessonPlayerState.currentLessonId
                    )
                );

            const quizQuestionsResponse =
                await getJson(
                    LLA_API_ENDPOINTS.admin.lessons.quizQuestions(
                        LessonPlayerState.currentLessonId
                    )
                );

            if (
                !lessonResponse.success ||
                !lessonResponse.lesson
            ) {
                throw new Error(
                    lessonResponse.error ||
                    messages.lessonNotFound
                );
            }

            LessonPlayerState.currentLesson =
                lessonResponse.lesson;

            LessonPlayerState.learningItems =
                learningItemsResponse.lessonLearningItems || [];

            LessonPlayerState.quizQuestions =
                quizQuestionsResponse.lessonQuizQuestions || [];

            if (
                LessonPlayerState.learningItems.length === 0
            ) {

                LessonPlayerRenderer.setMessage(
                    LessonPlayerState.currentLesson.title,
                    messages.noLearningItemsAssigned
                );

                return;
            }

            LessonPlayerRenderer.renderCurrentLearningItem();

            const roadmapElement =
                document.getElementById(
                    "pronunciationRoadmapMessage"
                );

            if (roadmapElement) {
                roadmapElement.textContent =
                    messages.pronunciationRoadmapMessage;
            }

        } catch (error) {

            LessonPlayerRenderer.setMessage(
                messages.couldNotLoadLesson,
                error.message ||
                messages.unknownError
            );
        }
    }


    function wireEvents() {

        addClickHandler(
            ids.previousLearningItemButton,
            LessonPlayerNavigation.goToPreviousLearningItem
        );

        addClickHandler(
            ids.nextLearningItemButton,
            LessonPlayerNavigation.goToNextLearningItem
        );

        addClickHandler(
            ids.backToStartLessonButton,
            LessonPlayerNavigation.goBackToStartLesson
        );

        addClickHandler(
            ids.moreExamplesButton,
            handleMoreExamples
        );

        addClickHandler(
            ids.playSoundButton,
            playCurrentSourceText
        );

        addClickHandler(
            ids.playEnglishSoundButton,
            playCurrentEnglishTranslation
        );

        addClickHandler(
            ids.playExampleSoundButton,
            playCurrentExampleText
        );

        addClickHandler(
            ids.playSecondExampleSoundButton,
            playSecondExampleText
        );

        addClickHandler(
            "startSpeechRecognitionButton",
            startSpeechRecognition
        );

        addClickHandler(
            ids.playThirdExampleSoundButton,
            playThirdExampleText
        );

        addClickHandler(
            ids.practicePronunciationButton,
            practiceCurrentPronunciation
        );

        addClickHandler(
            ids.favoriteLearningItemButton,
            LessonPlayerProgress.toggleFavorite
        );

        addClickHandler(
            ids.knowLearningItemButton,
            LessonPlayerProgress.markKnown
        );

        addClickHandler(
            ids.needsPracticeLearningItemButton,
            LessonPlayerProgress.markNeedsPractice
        );

        addClickHandler(
            ids.submitQuizAnswerButton,
            LessonPlayerQuiz.submitAnswer
        );

        addClickHandler(
            ids.nextQuizQuestionButton,
            LessonPlayerQuiz.goToNextQuestion
        );

        addClickHandler(
            "toneNeutralButton",
            setNeutralTone
        );

        addClickHandler(
            "toneEncouragingButton",
            setEncouragingTone
        );

        addClickHandler(
            "speedSlowButton",
            setSlowSpeed
        );

        addClickHandler(
            "speedNormalButton",
            setNormalSpeed
        );

        addClickHandler(
            "speedFastButton",
            setFastSpeed
        );
    }


    function init() {
        wireEvents();
        loadLessonPlayer();
    }


    return {
        init
    };

})();


LessonPlayerController.init();