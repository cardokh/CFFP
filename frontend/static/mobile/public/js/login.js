/*
 * Mobile login page controller.
 *
 * Responsibilities:
 * - Handle mobile login form submission.
 * - Validate required login fields.
 * - Call shared authentication API helpers.
 * - Store authenticated user data using shared session utilities.
 * - Navigate to register, forgot-password, demo, and welcome pages.
 * - Display mobile-friendly login feedback messages.
 */

const loginForm =
    document.getElementById("loginForm");

const errorText =
    document.getElementById("error");

const goToRegisterButton =
    document.getElementById("goToRegisterButton");

const forgotPasswordLink =
    document.getElementById("forgotPasswordLink");

const tryDemoButton =
    document.getElementById("tryDemoButton");

const REGISTER_SUCCESS_MESSAGE_KEY =
    "registerSuccessMessage";

function showLoginMessage(message, isSuccess = false) {
    errorText.textContent = message;
    errorText.style.color =
        isSuccess ? "#2f8f5b" : "#e05959";
}

function showRegisterSuccessMessage() {
    const successMessage =
        sessionStorage.getItem(
            REGISTER_SUCCESS_MESSAGE_KEY
        );

    if (!successMessage) {
        return;
    }

    showLoginMessage(
        successMessage,
        true
    );

    sessionStorage.removeItem(
        REGISTER_SUCCESS_MESSAGE_KEY
    );
}

function goToRegister() {
    window.location.href =
        window.LLA_PATHS.mobile.public.register;
}

function goToForgotPassword() {
    window.location.href =
        window.LLA_PATHS.mobile.public.forgotPassword;
}

function goToTryDemo() {
    window.location.href =
        window.LLA_PATHS.mobile.public.tryDemo;
}

function goToProtectedWelcome() {
    window.location.href =
        window.LLA_PATHS.mobile.protected.welcome;
}

async function handleLoginSubmit(event) {
    event.preventDefault();

    const email =
        document.getElementById("email").value.trim();

    const password =
        document.getElementById("password").value;

    if (!email) {
        showLoginMessage("Email is required.");
        return;
    }

    if (!password) {
        showLoginMessage("Password is required.");
        return;
    }

    showLoginMessage("");

    try {
        const result =
            await login(email, password);

        if (result.success) {
            saveAuthenticatedUser(result.user);

            goToProtectedWelcome();

            return;
        }

        showLoginMessage(
            mapLoginError(result.error)
        );

    } catch (error) {
        showLoginMessage(
            error.message || "Could not connect to the server."
        );

        console.error(error);
    }
}

loginForm.addEventListener(
    "submit",
    handleLoginSubmit
);

goToRegisterButton.addEventListener(
    "click",
    goToRegister
);

forgotPasswordLink.addEventListener(
    "click",
    goToForgotPassword
);

tryDemoButton.addEventListener(
    "click",
    goToTryDemo
);

showRegisterSuccessMessage();