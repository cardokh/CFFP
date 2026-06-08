# HejSan

HejSan is a language learning prototype focused on:
- protected learning workflows
- reusable web architecture
- language learning flows
- AI and HRI experimentation

This README only explains how to:
- clone the project
- initialize the development environment
- start the backend and frontend servers
- log in to the application

All other documentation, architecture overviews, workflows, AI/HRI vision,
and project presentation material are available inside the application through
the Project Guide.

---

## Clone the Project

```bash
git clone https://github.com/cardokh/LLA.git
cd LLA
```

---

## Initialize the Project

### Windows

```powershell
.\scripts\setup\bootstrap_project_windows.ps1
```

### macOS

```bash
bash scripts/setup/bootstrap_project_mac.sh
```

---

## Start the Backend

```bash
cd backend
python -m src.api.app
```

Backend runs on:

```text
http://127.0.0.1:8000
```

---

## Start the Frontend

Open a new terminal:

```bash
cd frontend/static
python -m http.server 5500
```

Frontend runs on:

```text
http://127.0.0.1:5500
```

---

## Login Credentials

### Admin User

```text
Email: admin@hejsan.local
Password: secret
```

### Demo Learner

```text
Email: demo@hejsan.local
Password: DemoPassword123
```

---

## Open the Application

Open:

```text
http://127.0.0.1:5500
```