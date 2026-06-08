/*
 * Lesson player examples helper.
 *
 * Responsibility:
 * - Build fallback examples.
 * - Load generated examples.
 * - Keep example-generation logic isolated.
 */

const LessonPlayerExamples = (() => {

    const fallback = LessonPlayerConstants.fallback;


    function getDisplayValue(value) {
        return value || fallback.emptyText;
    }


    function getCurrentLearningItem() {
        return LessonPlayerState.learningItems[
            LessonPlayerState.currentLearningItemIndex
        ];
    }


    function buildFallbackExamples(learningItem) {
        const sourceText =
            getDisplayValue(
                learningItem?.sourceText
            );

        return {
            second: {
                text: `Kan jag få ${sourceText.toLowerCase()}?`,
                translation:
                    fallback.secondExampleTranslation
            },

            third: {
                text: `Jag tycker om ${sourceText.toLowerCase()}.`,
                translation:
                    fallback.thirdExampleTranslation
            }
        };
    }


    async function loadGeneratedExamples() {
        const learningItem = getCurrentLearningItem();

        if (!learningItem || !learningItem.itemId) {
            LessonPlayerState.generatedExamples = [];
            return;
        }

        const response =
            await getJson(
                LLA_API_ENDPOINTS.admin.learningItems.examples(
                    learningItem.itemId
                )
            );

        if (
            !response.success ||
            !Array.isArray(response.generatedExamples)
        ) {
            LessonPlayerState.generatedExamples = [];
            return;
        }

        LessonPlayerState.generatedExamples =
            response.generatedExamples;
    }


    function getGeneratedExample(index) {
        return LessonPlayerState.generatedExamples[index] || null;
    }


    return {
        buildFallbackExamples,
        loadGeneratedExamples,
        getGeneratedExample
    };

})();