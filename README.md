# My First App

A tiny to-do list, built to learn three tools: **VS Code**, **Git + GitHub**, and **Claude Code**.
It needs only Python. There is nothing else to install to run it.

## How the pieces fit

```
Browser  ──────────►  frontend/        what you see and click (HTML, CSS, JavaScript)
                          │  asks "/api/tasks"
                          ▼
                      backend/server.py    the Python program that answers
                          │
                          ▼
                      data/tasks.db        the database file where tasks are kept
```

| File | What it is |
|---|---|
| `frontend/index.html` | The page structure: heading, text box, list |
| `frontend/style.css` | Colours, spacing, fonts |
| `frontend/app.js` | Sends your clicks to the backend and redraws the list |
| `backend/server.py` | Python: stores tasks and answers the frontend |
| `backend/test_server.py` | Automatic checks that the backend still works |
| `.gitignore` | Files Git should not save (your database, caches) |

## Run it

```powershell
python backend/server.py
```
Open http://localhost:8010. Press `Ctrl+C` in the terminal to stop it.

## Test it

```powershell
python -m unittest discover backend
```
`OK` at the end means all 10 checks passed.

---

## Lesson 1: VS Code

1. Open VS Code, then **File > Open Folder** and pick this `my-first-app` folder.
2. Left bar: the top icon is the **Explorer** (your files). Click `backend/server.py` to read it.
3. **Terminal > New Terminal** opens a command line at the bottom. Run the app from there.
4. If VS Code offers to install the **Python** extension, accept. It adds colours and error hints.
5. Change something small: in `frontend/index.html` change `My Tasks` to your own title,
   save (`Ctrl+S`), and refresh the browser.

## Lesson 2: Git (saving history on your computer)

Git is installed on this computer, and the first two steps below are already done for this
project. They are listed so you know what to do on a new computer or a new project.

Tell Git who you are (once per computer):
```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Then, in this folder:
```powershell
git init                 # start tracking this folder
git status               # what changed?
git add .                # choose everything to save
git commit -m "First version of my to-do app"
```
A **commit** is a saved snapshot you can always go back to. The loop from now on is:
change something, `git status`, `git add .`, `git commit -m "what I did"`.

In VS Code, the **Source Control** icon in the left bar (the branching lines) does the same with buttons.

## Lesson 3: GitHub (a copy online, to share)

1. Create a free account at https://github.com.
2. Click **+ > New repository**, name it `my-first-app`, leave everything else unticked, **Create**.
3. GitHub shows you two commands under "push an existing repository". They look like:
```powershell
git remote add origin https://github.com/YOUR-NAME/my-first-app.git
git push -u origin main
```
4. Refresh the GitHub page: your files are there. After that, `git push` uploads each new commit.

Later, try the team workflow: `git checkout -b my-change` (a **branch**), commit, `git push`,
then open a **pull request** on GitHub. That is how the City Planning OS project accepts changes.

## Lesson 4: Claude Code

Open this folder in Claude Code and ask in plain language. Good first requests:

- "Explain what `backend/server.py` does, step by step."
- "What happens when I click Add? Trace it from the browser to the database."
- "Add a due date to each task." (touches database, backend, frontend and tests)
- "Add a button that clears all finished tasks."
- "Run the tests and tell me what each one checks."
- "Commit my changes with a good message." (after Git is installed)

Habits worth forming: read the changes Claude makes before accepting them, ask "why" when
something is unclear, and commit after each working change so you can always go back.
