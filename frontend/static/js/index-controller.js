/*
 * Application entry page controller.
 *
 * Responsibilities:
 * - Handle interaction style selection.
 * - Persist the selected interaction style.
 * - Redirect the user to the correct public login interface.
 */

const mobileButton =
    document.getElementById("mobile-style-button");

const desktopButton =
    document.getElementById("desktop-style-button");

function getPublicLoginPath(style) {
    switch (style) {
        case InteractionStyle.MOBILE:
            return window.LLA_PATHS.mobile.public.login;

        case InteractionStyle.DESKTOP:
            return window.LLA_PATHS.desktop.public.login;

        default:
            console.error(
                "Unsupported interaction style:",
                style
            );

            return null;
    }
}

function redirectToPublicLogin(style) {
    const loginPath =
        getPublicLoginPath(style);

    if (!loginPath) {
        return;
    }

    window.location.href =
        loginPath;
}

mobileButton.addEventListener("click", function () {
    setInteractionStyle(
        InteractionStyle.MOBILE
    );

    redirectToPublicLogin(
        InteractionStyle.MOBILE
    );
});

desktopButton.addEventListener("click", function () {
    setInteractionStyle(
        InteractionStyle.DESKTOP
    );

    redirectToPublicLogin(
        InteractionStyle.DESKTOP
    );
});