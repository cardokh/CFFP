/*
 * Lesson player shared state.
 *
 * Responsibility:
 * - Hold shared lesson-player runtime state.
 * - Act as the single source of truth for lesson-player modules.
 */

const LessonPlayerState = {
    currentLessonId: null,
    currentLesson: null,

    learningItems: [],

    generatedExamples: [],

    currentLearningItemIndex: 0,

    itemProgressById: new Map(),

    quizQuestions: [],
    currentQuizQuestionIndex: 0,
    selectedQuizAnswerId: null,
    quizAnswersByQuestionId: new Map(),
    quizScore: 0,
    isQuizActive: false,
    isQuizComplete: false,
    isLessonComplete: false
};