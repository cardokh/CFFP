(function () {
    "use strict";

    const slides = Array.from(
        document.querySelectorAll(".presentation-slide")
    );

    const previousButton = document.getElementById(
        "previousSlideButton"
    );

    const nextButton = document.getElementById(
        "nextSlideButton"
    );

    const fullscreenButton = document.getElementById(
        "fullscreenButton"
    );

    const autoPlayButton = document.getElementById(
        "autoPlayButton"
    );

    const indicatorsContainer = document.getElementById(
        "slideIndicators"
    );

    const presentationStage = document.querySelector(
        ".presentation-stage"
    );

    let currentSlideIndex = 0;

    let autoPlayInterval = null;

    function updateNavigationButtons() {
        if (currentSlideIndex === 0) {
            previousButton.disabled = true;
        }
        else {
            previousButton.disabled = false;
        }

        if (currentSlideIndex === slides.length - 1) {
            nextButton.disabled = true;
        }
        else {
            nextButton.disabled = false;
        }
    }

    function showSlide(index) {
        if (index < 0) {
            index = 0;
        }

        if (index > slides.length - 1) {
            index = slides.length - 1;
        }

        currentSlideIndex = index;

        slides.forEach(function (slide, slideIndex) {
            slide.classList.toggle(
                "is-active",
                slideIndex === currentSlideIndex
            );
        });

        updateIndicators();

        updateNavigationButtons();
    }

    function createIndicators() {
        indicatorsContainer.innerHTML = "";

        slides.forEach(function (_, index) {
            const indicator = document.createElement("button");

            indicator.type = "button";

            indicator.className = "slide-indicator";

            indicator.setAttribute(
                "aria-label",
                "Go to slide " + (index + 1)
            );

            indicator.addEventListener("click", function () {
                stopAutoPlay();

                showSlide(index);
            });

            indicatorsContainer.appendChild(indicator);
        });
    }

    function updateIndicators() {
        const indicators = Array.from(
            document.querySelectorAll(".slide-indicator")
        );

        indicators.forEach(function (indicator, index) {
            indicator.classList.toggle(
                "is-active",
                index === currentSlideIndex
            );
        });
    }

    function showPreviousSlide() {
        stopAutoPlay();

        showSlide(currentSlideIndex - 1);
    }

    function showNextSlide() {
        stopAutoPlay();

        showSlide(currentSlideIndex + 1);
    }

    function updateFullscreenButton() {
        if (!fullscreenButton) {
            return;
        }

        if (document.fullscreenElement) {
            fullscreenButton.textContent = "Exit full screen";
        }
        else {
            fullscreenButton.textContent = "Full screen";
        }
    }

    function updateAutoPlayButton() {
        if (!autoPlayButton) {
            return;
        }

        if (autoPlayInterval) {
            autoPlayButton.textContent = "Stop auto";
        }
        else {
            autoPlayButton.textContent = "Auto play";
        }
    }

    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            presentationStage.requestFullscreen();
        }
        else {
            document.exitFullscreen();
        }
    }

    function startAutoPlay() {
        stopAutoPlay();

        autoPlayInterval = window.setInterval(function () {
            if (currentSlideIndex >= slides.length - 1) {
                stopAutoPlay();

                return;
            }

            showSlide(currentSlideIndex + 1);
        }, 6000);

        updateAutoPlayButton();
    }

    function stopAutoPlay() {
        if (autoPlayInterval) {
            window.clearInterval(autoPlayInterval);

            autoPlayInterval = null;
        }

        updateAutoPlayButton();
    }

    function toggleAutoPlay() {
        if (autoPlayInterval) {
            stopAutoPlay();
        }
        else {
            startAutoPlay();
        }
    }

    function handleKeyboard(event) {
        if (event.key === "ArrowLeft") {
            showPreviousSlide();
        }

        if (event.key === "ArrowRight") {
            showNextSlide();
        }

        if (event.key === "f" || event.key === "F") {
            toggleFullscreen();
        }

        if (event.key === " ") {
            event.preventDefault();

            toggleAutoPlay();
        }
    }

    function initializePresentation() {
        if (
            !slides.length ||
            !previousButton ||
            !nextButton ||
            !fullscreenButton ||
            !autoPlayButton ||
            !indicatorsContainer ||
            !presentationStage
        ) {
            return;
        }

        createIndicators();

        previousButton.addEventListener(
            "click",
            showPreviousSlide
        );

        nextButton.addEventListener(
            "click",
            showNextSlide
        );

        fullscreenButton.addEventListener(
            "click",
            toggleFullscreen
        );

        autoPlayButton.addEventListener(
            "click",
            toggleAutoPlay
        );

        document.addEventListener(
            "keydown",
            handleKeyboard
        );

        document.addEventListener(
            "fullscreenchange",
            updateFullscreenButton
        );

        showSlide(0);

        updateFullscreenButton();

        updateAutoPlayButton();
    }

    initializePresentation();
})();