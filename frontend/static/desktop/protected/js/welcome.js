< !DOCTYPE html >
    <html lang="en">

        <head>
            <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Welcome | HejSan</title>

                    <link rel="stylesheet" href="/desktop/shared/styles/protected-layout.css">
                        <link rel="stylesheet" href="./css/welcome.css">
                        </head>

                        <body>

                            <main class="dashboard-layout">

                                <div id="desktop-sidebar-container"></div>

                                <section class="main-content">

                                    <div class="welcome-content">

                                        <div id="header-panel-container"></div>

                                        <div class="protected-content-panel">

                                            <section class="welcome-panel">

                                                <div class="welcome-copy">

                                                    <p class="welcome-eyebrow">
                                                        Welcome back
                                                    </p>

                                                    <h1>
                                                        Pick up your Swedish practice gently.
                                                    </h1>

                                                    <p class="welcome-description">
                                                        Start a lesson, check your progress, or continue
                                                        with a short focused practice session.
                                                    </p>

                                                    <div class="welcome-actions">

                                                        <a class="welcome-primary-action" href="/desktop/protected/available-lessons.html">
                                                            Open Lesson Library
                                                        </a>

                                                        <a class="welcome-secondary-action" href="/desktop/protected/progress.html">
                                                            View Progress
                                                        </a>

                                                    </div>

                                                </div>

                                                <div class="welcome-animation" aria-hidden="true">

                                                    <div class="calm-orbit orbit-large"></div>
                                                    <div class="calm-orbit orbit-small"></div>

                                                    <div class="calm-robot">
                                                        🤖
                                                    </div>

                                                    <div class="calm-chip chip-hej">
                                                        hej
                                                    </div>

                                                    <div class="calm-chip chip-bra">
                                                        bra
                                                    </div>

                                                    <div class="calm-chip chip-tack">
                                                        tack
                                                    </div>

                                                </div>

                                                <div class="welcome-cards">

                                                    <article class="welcome-card">
                                                        <span>01</span>
                                                        <strong>Choose</strong>
                                                        <p>Select a lesson from your library.</p>
                                                    </article>

                                                    <article class="welcome-card">
                                                        <span>02</span>
                                                        <strong>Practice</strong>
                                                        <p>Listen, repeat, and answer a few questions.</p>
                                                    </article>

                                                    <article class="welcome-card">
                                                        <span>03</span>
                                                        <strong>Continue</strong>
                                                        <p>Use your progress to decide what comes next.</p>
                                                    </article>

                                                </div>

                                            </section>

                                        </div>

                                        <div id="footer-panel-container"></div>

                                    </div>

                                </section>

                            </main>

                            <script src="/desktop/protected/shared/components/protected-workspace/protected-workspace.js"></script>

                            <script>
                                loadProtectedWorkspace("dashboard");
                            </script>

                            <script src="./js/welcome.js"></script>

                        </body>

                    </html>