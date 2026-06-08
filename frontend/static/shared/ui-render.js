/*
 * Shared UI rendering utilities.
 *
 * Purpose:
 * Provides reusable helpers for safely rendering user-controlled
 * values into HTML templates.
 *
 * Why this exists:
 * Some CRUD pages render values such as display names and emails
 * using innerHTML. If those values contain HTML-like characters,
 * they must be escaped before being inserted into the page.
 *
 * This protects the frontend from accidental or malicious HTML
 * injection while keeping controller code clean and reusable.
 */

function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}