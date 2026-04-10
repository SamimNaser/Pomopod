# PomoPod

A pomodoro where you can join pods with your friends and collaborate freely.

Features:

- Pomodoro timer
- Customizable timer settings and duration
- Host/join pods with friends
- Dark/light theme

## Dependenccies

**Important**: This project uses `uv` for Python and `pnpm` for React!

Install python dependencies and create virtual environment:

```bash
cd backend
uv sync
```

Install react and dependencies:

```bash
cd frontend
pnpm install
```

## Run the app

Run the backend:

```bash
cd backend
uv run pomopod --help
```

or

```bash
cd backend
source .venv/bin/activate
pomopod --help
```

Run the frontend:

```bash
cd frontend
pnpm dev
```
