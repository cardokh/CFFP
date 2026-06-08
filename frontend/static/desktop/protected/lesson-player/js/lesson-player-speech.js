/*
 * Lesson player speech helper.
 *
 * Responsibility:
 * - Speak lesson-player text using the browser SpeechSynthesis API.
 * - Recognize spoken practice text using the browser SpeechRecognition API.
 * - Keep speech configuration and pronunciation logic isolated.
 * - Apply selected pronunciation speed and tone settings.
 */

const LessonPlayerSpeech = (() => {

    const pronunciationSettings = {
        speed: "normal",
        tone: "neutral"
    };


    function isSpeechAvailable() {
        return Boolean(window.speechSynthesis);
    }


    function getSpeechRecognitionConstructor() {
        return window.SpeechRecognition ||
            window.webkitSpeechRecognition;
    }


    function isSpeechRecognitionAvailable() {
        return Boolean(
            getSpeechRecognitionConstructor()
        );
    }


    function getRateForSpeed(speed) {

        if (speed === "slow") {
            return LessonPlayerConstants.speech.slowRate;
        }

        if (speed === "fast") {
            return LessonPlayerConstants.speech.fastRate;
        }

        return LessonPlayerConstants.speech.normalRate;
    }


    function getPitchForTone(tone) {

        if (tone === "encouraging") {
            return LessonPlayerConstants.speech.encouragingPitch;
        }

        return LessonPlayerConstants.speech.neutralPitch;
    }


    function speak(
        text,
        language,
        rate,
        pitch
    ) {

        if (!text || !isSpeechAvailable()) {
            return;
        }

        window.speechSynthesis.cancel();

        const utterance =
            new SpeechSynthesisUtterance(
                text
            );

        utterance.lang =
            language;

        utterance.rate =
            rate;

        utterance.pitch =
            pitch;

        window.speechSynthesis.speak(
            utterance
        );
    }


    function speakSwedish(text) {

        speak(
            text,
            LessonPlayerConstants.speech.swedishLanguage,
            getRateForSpeed(
                pronunciationSettings.speed
            ),
            getPitchForTone(
                pronunciationSettings.tone
            )
        );
    }


    function speakSwedishSlowly(text) {

        speak(
            text,
            LessonPlayerConstants.speech.swedishLanguage,
            LessonPlayerConstants.speech.slowRate,
            getPitchForTone(
                pronunciationSettings.tone
            )
        );
    }


    function speakSwedishPractice(text) {

        speak(
            text,
            LessonPlayerConstants.speech.swedishLanguage,
            getRateForSpeed(
                pronunciationSettings.speed
            ),
            getPitchForTone(
                pronunciationSettings.tone
            )
        );
    }


    function speakEnglish(text) {

        speak(
            text,
            LessonPlayerConstants.speech.englishLanguage,
            LessonPlayerConstants.speech.normalRate,
            LessonPlayerConstants.speech.neutralPitch
        );
    }


    function recognizeSwedishSpeech(
        onResult,
        onError,
        onStart,
        onEnd
    ) {

        const SpeechRecognitionConstructor =
            getSpeechRecognitionConstructor();

        if (!SpeechRecognitionConstructor) {

            if (onError) {
                onError(
                    "Speech recognition is not available in this browser."
                );
            }

            return;
        }

        const recognition =
            new SpeechRecognitionConstructor();

        recognition.lang =
            LessonPlayerConstants.speech.swedishLanguage;

        recognition.interimResults =
            false;

        recognition.continuous =
            false;

        recognition.maxAlternatives =
            1;

        recognition.onstart = () => {

            if (onStart) {
                onStart();
            }
        };

        recognition.onresult = (event) => {

            let transcript = "";

            for (
                let index = 0;
                index < event.results.length;
                index += 1
            ) {

                transcript +=
                    event.results[index][0].transcript + " ";
            }

            transcript =
                transcript.trim();

            if (onResult) {
                onResult(transcript);
            }
        };

        recognition.onerror = (event) => {

            if (!onError) {
                return;
            }

            if (event.error === "no-speech") {

                onError(
                    "No speech detected. Try again."
                );

                return;
            }

            if (event.error === "audio-capture") {

                onError(
                    "Microphone not available."
                );

                return;
            }

            if (event.error === "not-allowed") {

                onError(
                    "Microphone permission denied."
                );

                return;
            }

            if (event.error === "network") {

                onError(
                    "Browser speech recognition is unavailable. Please try Chrome."
                );

                return;
            }

            onError(
                "Could not recognize speech."
            );
        };

        recognition.onend = () => {

            if (onEnd) {
                onEnd();
            }
        };

        recognition.start();
    }


    function setSpeed(speed) {

        pronunciationSettings.speed =
            speed || "normal";
    }


    function setTone(tone) {

        pronunciationSettings.tone =
            tone || "neutral";
    }


    function getSettings() {

        return {
            ...pronunciationSettings
        };
    }


    return {
        speakSwedish,
        speakSwedishSlowly,
        speakSwedishPractice,
        speakEnglish,
        recognizeSwedishSpeech,
        isSpeechRecognitionAvailable,
        setSpeed,
        setTone,
        getSettings
    };

})();