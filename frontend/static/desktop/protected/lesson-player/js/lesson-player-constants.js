/*
 * Lesson player constants.
 *
 * Responsibility:
 * - Centralize lesson-player element IDs, labels, messages, speech settings,
 *   route fragments, and fallback values.
 * - Avoid scattered hardcoded strings across lesson-player modules.
 */

const LessonPlayerConstants = {
    elementIds: {
        lessonPlayerTitle: "lessonPlayerTitle",
        lessonPlayerProgressText: "lessonPlayerProgressText",

        sourceText: "sourceText",
        englishTranslation: "englishTranslation",
        pronunciationText: "pronunciationText",

        exampleText: "exampleText",
        exampleTranslationText: "exampleTranslationText",

        secondExampleText: "secondExampleText",
        secondExampleTranslationText: "secondExampleTranslationText",

        thirdExampleText: "thirdExampleText",
        thirdExampleTranslationText: "thirdExampleTranslationText",

        quizPanel: "quizPanel",
        quizQuestionText: "quizQuestionText",
        quizAnswerOptions: "quizAnswerOptions",
        quizFeedbackText: "quizFeedbackText",
        quizScoreText: "quizScoreText",

        lessonCompletedPanel: "lessonCompletedPanel",
        lessonCompletedTitle: "lessonCompletedTitle",
        lessonCompletedMessage: "lessonCompletedMessage",

        submitQuizAnswerButton: "submitQuizAnswerButton",
        nextQuizQuestionButton: "nextQuizQuestionButton",

        previousLearningItemButton: "previousLearningItemButton",
        nextLearningItemButton: "nextLearningItemButton",
        backToStartLessonButton: "backToStartLessonButton",

        moreExamplesButton: "moreExamplesButton",

        playSoundButton: "playSoundButton",
        playEnglishSoundButton: "playEnglishSoundButton",
        playExampleSoundButton: "playExampleSoundButton",
        playSecondExampleSoundButton: "playSecondExampleSoundButton",
        playThirdExampleSoundButton: "playThirdExampleSoundButton",

        slowPronunciationButton: "slowPronunciationButton",
        practicePronunciationButton: "practicePronunciationButton",
        favoriteLearningItemButton: "favoriteLearningItemButton",
        knowLearningItemButton: "knowLearningItemButton",
        needsPracticeLearningItemButton: "needsPracticeLearningItemButton"
    },

    panels: {
        lessonPlayerContent: {
            name: "lesson-player-content-panel",
            hasFieldset: true,
            fieldsetText: "Lesson player"
        },

        toolbar: {
            name: "toolbar-panel",
            hasFieldset: false,
            fieldsetText: null
        },

        currentLesson: {
            name: "current-lesson-panel",
            hasFieldset: true,
            fieldsetText: "Current lesson"
        },

        swedish: {
            name: "swedish-panel",
            hasFieldset: true,
            fieldsetText: "Swedish"
        },

        english: {
            name: "english-panel",
            hasFieldset: true,
            fieldsetText: "English"
        },

        pronunciation: {
            name: "pronunciation-panel",
            hasFieldset: true,
            fieldsetText: "Pronunciation"
        },

        learningItem: {
            name: "learning-item-panel",
            hasFieldset: true,
            fieldsetText: "Learning item"
        },

        practice: {
            name: "practice-panel",
            hasFieldset: true,
            fieldsetText: "Practice"
        },

        mainExample: {
            name: "main-example-panel",
            hasFieldset: false,
            fieldsetText: null
        },

        secondExample: {
            name: "second-example-panel",
            hasFieldset: false,
            fieldsetText: null
        },

        thirdExample: {
            name: "third-example-panel",
            hasFieldset: false,
            fieldsetText: null
        },

        pronunciationOptions: {
            name: "pronunciation-options-panel",
            hasFieldset: true,
            fieldsetText: "Pronunciation options"
        },

        quiz: {
            name: "quiz-panel",
            hasFieldset: true,
            fieldsetText: "Quiz"
        },

        tone: {
            name: "tone-panel",
            hasFieldset: true,
            fieldsetText: "Tone"
        },

        speed: {
            name: "speed-panel",
            hasFieldset: true,
            fieldsetText: "Speed"
        },

        accent: {
            name: "accent-panel",
            hasFieldset: true,
            fieldsetText: "Accent"
        },

        speechProvider: {
            name: "speech-provider-panel",
            hasFieldset: true,
            fieldsetText: "Speech provider"
        },

        aiRoadmap: {
            name: "ai-roadmap-panel",
            hasFieldset: true,
            fieldsetText: "AI roadmap"
        }
    },

    labels: {
        favorite: "♡ Favorite",
        favoriteSelected: "♥ Favorite",
        knowIt: "✓ Know it",
        known: "✓ Known",
        needsPractice: "⟳ Needs practice",
        needsPracticeSelected: "⟳ Needs practice ✓",
        practicePronunciation: "🎤 AI pronunciation practice",
        practiced: "〰 Practiced",
        next: "Next",
        finishLesson: "Finish lesson",
        startQuiz: "Start quiz",
        nextQuestion: "Next question",
        finishQuiz: "Finish quiz",
        submitAnswer: "Submit answer",
        moreExamples: "AI examples roadmap",
        loading: "Loading..."
    },

    messages: {
        lessonIdMissingTitle: "Lesson ID missing.",
        lessonIdMissingBody: "Could not find the lesson to start.",
        lessonNotFound: "Lesson not found.",
        noLearningItemsAssigned: "No learning items assigned.",
        couldNotLoadLesson: "Could not load lesson.",
        unknownError: "Unknown error.",
        couldNotLoadMoreExamples: "Could not load more examples.",
        failedToCompleteLesson: "Failed to complete lesson.",
        authenticatedUserIdMissing: "Authenticated user ID is missing.",
        noQuizQuestionsAvailable: "No quiz questions are available for this lesson.",

        quizUnavailableLessonWillComplete:
            "This lesson does not contain enough quiz content to start a quiz. The lesson will now be completed without a quiz.",

        chooseQuizAnswer: "Please choose an answer first.",
        correctQuizAnswer: "Correct.",
        incorrectQuizAnswer: "Not quite. The correct answer is:",
        quizComplete: "Quiz complete.",

        lessonCompletedTitle: "Congratulations!",
        lessonCompletedWithQuiz:
            "You have completed this lesson.",
        lessonCompletedWithoutQuiz:
            "You have completed this lesson without a quiz because there was not enough quiz content.",

        pronunciationRoadmapMessage:
            "AI-powered learning features are currently disabled because " +
            "we are not yet using a real AI backend or AI integration " +
            "for e-learning features.",
    },

    fallback: {
        emptyText: "—",
        lessonTitle: "Lesson",
        secondExampleTranslation: "Can I get this politely?",
        thirdExampleTranslation: "Express a simple preference."
    },

    speech: {
        swedishLanguage: "sv-SE",
        englishLanguage: "en-US",

        slowRate: 0.55,
        normalRate: 0.9,
        fastRate: 1.65,

        practiceRate: 0.8,

        neutralPitch: 0.9,
        encouragingPitch: 1.3
    },

    routes: {
        startLessonPath: "/desktop/protected/start-lesson.html"
    },

    queryParams: {
        lessonId: "lessonId"
    }
};