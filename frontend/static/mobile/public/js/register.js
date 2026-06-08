/*
 * Mobile registration page controller.
 *
 * Responsibilities:
 * - Handle mobile registration form submission
 * - Validate registration input before calling the backend
 * - Send account data to the registration API
 * - Show mobile-friendly registration feedback
 * - Redirect successful registrations to the login page
 */

const registerForm = document.getElementById("registerForm");
const registerMessage = document.getElementById("registerMessage");
const goToLoginButton = document.getElementById("goToLoginButton");

const REGISTER_SUCCESS_MESSAGE_KEY = "registerSuccessMessage";

function showRegisterMessage(message, isSuccess = false) {
    registerMessage.textContent = message;
    registerMessage.style.color = isSuccess ? "#2f8f5b" : "#d64545";
}

function goToLogin() {
    window.location.href = "./login.html";
}

function validateRegisterForm(
    displayName,
    email,
    password,
    confirmPassword
) {
    if (!displayName || !email || !password || !confirmPassword) {
        return "Please fill in all fields.";
    }

    if (displayName.length < 2) {
        return "Display name must be at least 2 characters.";
    }

    if (!email.includes("@")) {
        return "Please enter a valid email address.";
    }

    if (password.length < 8) {
        return "Password must be at least 8 characters.";
    }

    if (password !== confirmPassword) {
        return "Passwords do not match.";
    }

    return null;
}

async function handleRegisterSubmit(event) {
    event.preventDefault();

    const displayName =
        document.getElementById("displayName").value.trim();

    const email =
        document.getElementById("email").value.trim();

    const password =
        document.getElementById("password").value;

    const confirmPassword =
        document.getElementById("confirmPassword").value;

    const validationError = validateRegisterForm(
        displayName,
        email,
        password,
        confirmPassword
    );

    if (validationError) {
        showRegisterMessage(validationError);
        return;
    }

    showRegisterMessage("");

    try {
        const result = await postJson(
            LLA_API_ENDPOINTS.auth.register,
            {
                displayName: displayName,
                email: email,
                password: password,
                confirmPassword: confirmPassword
            }
        );

        if (result.success) {
            sessionStorage.setItem(
                REGISTER_SUCCESS_MESSAGE_KEY,
                "Account created successfully. You can now sign in."
            );

            window.location.href = "./login.html";
            return;
        }

        showRegisterMessage(
            result.error || "Registration failed."
        );

    } catch (error) {
        showRegisterMessage(
            "Could not connect to the server."
        );

        console.error(error);
    }
}

registerForm.addEventListener(
    "submit",
    handleRegisterSubmit
);

goToLoginButton.addEventListener(
    "click",
    goToLogin
);