/*
 * Lesson player progress helper.
 *
 * Responsibility:
 * - Track learning-item progress state.
 * - Handle favorite / known / needs-practice states.
 * - Update toolbar button labels.
 */

const LessonPlayerProgress = (() => {

    const ids = LessonPlayerConstants.elementIds;
    const labels = LessonPlayerConstants.labels;


    function getCurrentLearningItem() {
        return LessonPlayerState.learningItems[
            LessonPlayerState.currentLearningItemIndex
        ];
    }


    function getCurrentLearningItemKey() {
        const learningItem = getCurrentLearningItem();

        return String(
            learningItem?.itemId ||
            learningItem?.learningItemId ||
            LessonPlayerState.currentLearningItemIndex
        );
    }


    function getCurrentProgress() {
        const key = getCurrentLearningItemKey();

        if (!LessonPlayerState.itemProgressById.has(key)) {

            LessonPlayerState.itemProgressById.set(key, {
                favorite: false,
                known: false,
                needsPractice: false,
                practiced: false
            });
        }

        return LessonPlayerState.itemProgressById.get(key);
    }


    function updateButtons() {
        const progress = getCurrentProgress();

        const favoriteButton =
            document.getElementById(
                ids.favoriteLearningItemButton
            );

        const knowButton =
            document.getElementById(
                ids.knowLearningItemButton
            );

        const needsPracticeButton =
            document.getElementById(
                ids.needsPracticeLearningItemButton
            );

        const practiceButton =
            document.getElementById(
                ids.practicePronunciationButton
            );


        if (favoriteButton) {
            favoriteButton.textContent =
                progress.favorite
                    ? labels.favoriteSelected
                    : labels.favorite;
        }


        if (knowButton) {
            knowButton.textContent =
                progress.known
                    ? labels.known
                    : labels.knowIt;
        }


        if (needsPracticeButton) {
            needsPracticeButton.textContent =
                progress.needsPractice
                    ? labels.needsPracticeSelected
                    : labels.needsPractice;
        }


        if (practiceButton) {
            practiceButton.textContent =
                progress.practiced
                    ? labels.practiced
                    : labels.practicePronunciation;
        }
    }


    function toggleFavorite() {
        const progress = getCurrentProgress();

        progress.favorite = !progress.favorite;

        updateButtons();
    }


    function markKnown() {
        const progress = getCurrentProgress();

        progress.known = true;
        progress.needsPractice = false;

        updateButtons();
    }


    function markNeedsPractice() {
        const progress = getCurrentProgress();

        progress.needsPractice = true;
        progress.known = false;

        updateButtons();
    }


    function markPronunciationPracticed() {
        const progress = getCurrentProgress();

        progress.practiced = true;

        updateButtons();
    }


    return {
        getCurrentProgress,
        updateButtons,
        toggleFavorite,
        markKnown,
        markNeedsPractice,
        markPronunciationPracticed
    };

})();