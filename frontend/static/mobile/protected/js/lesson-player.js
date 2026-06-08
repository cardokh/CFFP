const LESSON_PLAYER_TITLE_ID =
    "lessonPlayerTitle";

const LESSON_PLAYER_PROGRESS_TEXT_ID =
    "lessonPlayerProgressText";

const SOURCE_TEXT_ID =
    "sourceText";

const ENGLISH_TRANSLATION_ID =
    "englishTranslation";

const PRONUNCIATION_TEXT_ID =
    "pronunciationText";

const EXAMPLE_TEXT_ID =
    "exampleText";

const EXAMPLE_TRANSLATION_TEXT_ID =
    "exampleTranslationText";

const PREVIOUS_BUTTON_ID =
    "previousLearningItemButton";

const NEXT_BUTTON_ID =
    "nextLearningItemButton";

const EXIT_BUTTON_ID =
    "backToStartLessonButton";

const PLAY_SOUND_BUTTON_ID =
    "playSoundButton";

const PLAY_ENGLISH_SOUND_BUTTON_ID =
    "playEnglishSoundButton";

const PLAY_EXAMPLE_SOUND_BUTTON_ID =
    "playExampleSoundButton";


let currentLessonId = null;

let currentLesson = null;

let learningItems = [];

let currentLearningItemIndex = 0;


function getElement(id) {
    return document.getElementById(id);
}

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

    const user =
        requireAuthentication();

    if (!user?.userId) {

        throw new Error(
            "Authenticated user ID is missing."
        );
    }

    return user.userId;
}

function getDisplayValue(value) {
    return value || "—";
}

function getCurrentLearningItem() {
    return learningItems[
        currentLearningItemIndex
    ];
}


function goBackToStartLesson() {

    window.location.href =
        `/mobile/protected/start-lesson.html?lessonId=${currentLessonId}`;
}

function navigateBackToMyLessons() {

    window.location.href =
        "/mobile/protected/available-lessons.html";
}

function speakText(
    text,
    language = "sv-SE"
) {

    if (
        !text ||
        !window.speechSynthesis
    ) {
        return;
    }

    window.speechSynthesis.cancel();

    window.speechSynthesis.resume();

    const utterance =
        new SpeechSynthesisUtterance(
            text
        );

    utterance.lang = language;

    window.speechSynthesis.speak(
        utterance
    );
}

function playCurrentSourceText() {

    const item =
        getCurrentLearningItem();

    speakText(
        item?.sourceText,
        "sv-SE"
    );
}

function playCurrentEnglishTranslation() {

    const item =
        getCurrentLearningItem();

    speakText(
        item?.englishTranslation,
        "en-US"
    );
}

function playCurrentExampleText() {

    const item =
        getCurrentLearningItem();

    speakText(
        item?.exampleText,
        "sv-SE"
    );
}

function renderLearningItem() {

    if (!learningItems.length) {
        return;
    }

    const item =
        getCurrentLearningItem();

    const lessonTitle =
        getElement(
            LESSON_PLAYER_TITLE_ID
        );

    const progressText =
        getElement(
            LESSON_PLAYER_PROGRESS_TEXT_ID
        );

    const sourceText =
        getElement(
            SOURCE_TEXT_ID
        );

    const englishTranslation =
        getElement(
            ENGLISH_TRANSLATION_ID
        );

    const pronunciationText =
        getElement(
            PRONUNCIATION_TEXT_ID
        );

    const exampleText =
        getElement(
            EXAMPLE_TEXT_ID
        );

    const exampleTranslationText =
        getElement(
            EXAMPLE_TRANSLATION_TEXT_ID
        );

    if (lessonTitle) {

        lessonTitle.textContent =
            currentLesson.title || "Lesson";
    }

    if (progressText) {

        progressText.textContent =
            `Item ${currentLearningItemIndex + 1} of ${learningItems.length}`;
    }

    if (sourceText) {

        sourceText.textContent =
            getDisplayValue(
                item.sourceText
            );
    }

    if (englishTranslation) {

        englishTranslation.textContent =
            getDisplayValue(
                item.englishTranslation
            );
    }

    if (pronunciationText) {

        pronunciationText.textContent =
            getDisplayValue(
                item.pronunciation
            );
    }

    if (exampleText) {

        exampleText.textContent =
            getDisplayValue(
                item.exampleText
            );
    }

    if (exampleTranslationText) {

        exampleTranslationText.textContent =
            getDisplayValue(
                item.englishTranslation
            );
    }

    updateNavigationButtons();
}


function updateNavigationButtons() {

    const previousButton =
        getElement(
            PREVIOUS_BUTTON_ID
        );

    const nextButton =
        getElement(
            NEXT_BUTTON_ID
        );

    if (previousButton) {

        previousButton.disabled =
            currentLearningItemIndex === 0;
    }

    if (!nextButton) {
        return;
    }

    const isLastItem =
        currentLearningItemIndex ===
        learningItems.length - 1;

    if (isLastItem) {

        nextButton.textContent =
            "Finish lesson";

    } else {

        nextButton.textContent =
            "Next";
    }
}

function goToPreviousLearningItem() {

    if (
        currentLearningItemIndex === 0
    ) {
        return;
    }

    currentLearningItemIndex--;

    renderLearningItem();
}

async function goToNextLearningItem() {

    const isLastItem =
        currentLearningItemIndex >=
        learningItems.length - 1;

    if (isLastItem) {

        await markLessonCompleted();

        navigateBackToMyLessons();

        return;
    }

    currentLearningItemIndex++;

    renderLearningItem();
}


async function markLessonCompleted() {

    const userId =
        getAuthenticatedUserId();

    const response =
        await postJson(
            LLA_API_ENDPOINTS
                .admin
                .userLessons
                .markCompleted(userId),

            {
                lesson_id:
                currentLessonId
            }
        );

    if (!response.success) {

        throw new Error(
            response.error
        );
    }
}

function toggleSection(
    sectionId,
    buttonId,
    label
) {

    const section =
        getElement(sectionId);

    const button =
        getElement(buttonId);

    if (
        !section ||
        !button
    ) {
        return;
    }

    const isHidden =
        section.classList.contains(
            "hidden-section"
        );

    if (isHidden) {

        section.classList.remove(
            "hidden-section"
        );

        button.textContent =
            `Hide ${label}`;

    } else {

        section.classList.add(
            "hidden-section"
        );

        button.textContent =
            `Show ${label}`;
    }
}

function togglePronunciation() {

    const pronunciationText =
        getElement(
            PRONUNCIATION_TEXT_ID
        );

    const button =
        getElement(
            "togglePronunciationBtn"
        );

    if (
        !pronunciationText ||
        !button
    ) {
        return;
    }

    const isHidden =
        pronunciationText.classList.contains(
            "hidden-section"
        );

    if (isHidden) {

        pronunciationText.classList.remove(
            "hidden-section"
        );

        button.textContent =
            "Hide pronunciation";

    } else {

        pronunciationText.classList.add(
            "hidden-section"
        );

        button.textContent =
            "Show pronunciation";
    }
}


async function loadLessonPlayer() {

    try {

        currentLessonId =
            getLessonIdFromUrl();

        if (!currentLessonId) {
            return;
        }

        const lessonResponse =
            await getJson(
                LLA_API_ENDPOINTS
                    .admin
                    .lessons
                    .byId(currentLessonId)
            );

        const learningItemsResponse =
            await getJson(
                LLA_API_ENDPOINTS
                    .admin
                    .lessons
                    .learningItems(currentLessonId)
            );

        currentLesson =
            lessonResponse.lesson;

        learningItems =
            learningItemsResponse
                .lessonLearningItems || [];

        renderLearningItem();

    } catch (error) {

        console.error(
            "Failed to load lesson player:",
            error
        );

        const messageElement =
            getElement(
                "lessonPlayerMessage"
            );

        if (messageElement) {

            messageElement.textContent =
                "Failed to load lesson.";

            messageElement.classList.remove(
                "hidden"
            );
        }
    }
}


function addClickListener(
    elementId,
    handler
) {

    const element =
        getElement(elementId);

    if (!element) {
        return;
    }

    element.addEventListener(
        "click",
        handler
    );
}

function startPractice() {

    const item =
        getCurrentLearningItem();

    if (!item) {
        return;
    }

    speakText(
        item.sourceText,
        "sv-SE"
    );

    alert(
        "Repeat after the pronunciation."
    );
}

addClickListener(
    "startPracticeButton",
    startPractice
);

/* Navigation */

addClickListener(
    PREVIOUS_BUTTON_ID,
    goToPreviousLearningItem
);

addClickListener(
    NEXT_BUTTON_ID,
    goToNextLearningItem
);

addClickListener(
    EXIT_BUTTON_ID,
    goBackToStartLesson
);

/* Audio */

addClickListener(
    PLAY_SOUND_BUTTON_ID,
    playCurrentSourceText
);

addClickListener(
    PLAY_ENGLISH_SOUND_BUTTON_ID,
    playCurrentEnglishTranslation
);

addClickListener(
    PLAY_EXAMPLE_SOUND_BUTTON_ID,
    playCurrentExampleText
);

/* Toggles */

addClickListener(
    "toggleTranslationBtn",
    () => {

        toggleSection(
            "translationSection",
            "toggleTranslationBtn",
            "translation"
        );
    }
);

addClickListener(
    "toggleExamplesBtn",
    () => {

        toggleSection(
            "examplesSection",
            "toggleExamplesBtn",
            "examples"
        );
    }
);

addClickListener(
    "togglePronunciationBtn",
    togglePronunciation
);

loadLessonPlayer();
