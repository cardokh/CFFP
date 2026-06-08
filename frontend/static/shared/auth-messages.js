/*
 * Shared authentication message helpers.
 *
 * Responsibilities:
 * - Convert backend authentication error codes into user-friendly frontend messages.
 * - Centralize reusable authentication messaging.
 * - Keep authentication page controllers free from error-code mapping logic.
 *
 * Architectural rules:
 * - Authentication controllers should not hardcode backend auth error codes.
 * - Backend auth error codes should be mapped here before being shown to users.
 */

const LLA_AUTH_ERROR_CODES = {
    userNotFound: "USER_NOT_FOUND",
    invalidPassword: "INVALID_PASSWORD",
    userInactive: "USER_INACTIVE",
    userNotVerified: "USER_NOT_VERIFIED"
};

const LLA_AUTH_MESSAGES = {
    incorrectCredentials: "Incorrect email or password.",
    inactiveAccount: "This account is inactive.",
    unverifiedAccount: "Please verify your account before signing in.",
    loginFailed: "Login failed. Please try again."
};

function mapLoginError(errorCode) {
    switch (errorCode) {
        case LLA_AUTH_ERROR_CODES.userNotFound:
        case LLA_AUTH_ERROR_CODES.invalidPassword:
            return LLA_AUTH_MESSAGES.incorrectCredentials;

        case LLA_AUTH_ERROR_CODES.userInactive:
            return LLA_AUTH_MESSAGES.inactiveAccount;

        case LLA_AUTH_ERROR_CODES.userNotVerified:
            return LLA_AUTH_MESSAGES.unverifiedAccount;

        default:
            return LLA_AUTH_MESSAGES.loginFailed;
    }
}