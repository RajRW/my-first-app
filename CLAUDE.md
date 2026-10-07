# My First App: Claude guidance

A small to-do list app that Raj uses to learn VS Code, Git, GitHub and Claude Code.
Raj is new to programming: explain what you do and why in plain language, name the Git
command behind each step, and keep changes small enough to read in one sitting.

## Layout
- `backend/server.py`: Python web server, JSON API under `/api/tasks`, SQLite storage.
  The database functions at the top are the only code that touches the `tasks` table.
- `backend/test_server.py`: `unittest` tests for the database functions and the API.
- `frontend/index.html`, `style.css`, `app.js`: plain HTML, CSS and JavaScript. No build step.
- `data/tasks.db`: created on first run, holds Raj's own tasks, ignored by Git.

## Commands
```powershell
python backend/server.py               # run the app at http://localhost:8010
python -m unittest discover backend    # run the tests
```

## Rules
- Standard library only. Do not add pip or npm packages without asking first.
- A change to the backend comes with a test. Run the tests before every commit; all must pass.
- A change the user can see is checked in the browser, not only by the tests.
- When testing in the browser, add your own temporary task and remove it afterwards.
  Never tick, edit or delete the tasks already in the list.
- Keep the code simple and commented for a beginner. No frameworks, no clever shortcuts.

## Git workflow
- Never commit straight to `main`. Create a branch, commit, push the branch, and leave opening
  and merging the pull request on GitHub to Raj (that is part of the learning).
- Commit messages: one short line saying what changed, in plain words.
- Commits must use the private address `335454495+RajRW@users.noreply.github.com`.
  Never put Raj's real email address in a commit, a file or a pull request.
- Do not rewrite history that has been pushed (no force push, no rebase of pushed commits).
- Remote: https://github.com/RajRW/my-first-app
