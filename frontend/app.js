// Frontend for My First App.
// It never touches the database itself: it asks the backend through /api/tasks
// and then redraws the list with whatever the backend says.

const list = document.getElementById("tasks");
const form = document.getElementById("add-form");
const titleInput = document.getElementById("title");
const summary = document.getElementById("summary");
const errorBox = document.getElementById("error");

// Send a request to the backend and return its JSON answer.
async function api(method, path, body) {
  const response = await fetch(path, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong");
  return data;
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = !message;
}

function render(tasks) {
  list.innerHTML = "";

  const left = tasks.filter((task) => !task.done).length;
  summary.textContent = tasks.length ? `${left} of ${tasks.length} left to do` : "";

  if (tasks.length === 0) {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = "Nothing here yet. Add your first task above.";
    list.append(empty);
    return;
  }

  for (const task of tasks) {
    const item = document.createElement("li");
    item.className = task.done ? "done" : "";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.id = `task-${task.id}`;
    checkbox.checked = task.done;
    checkbox.addEventListener("change", () =>
      change(() => api("PATCH", `/api/tasks/${task.id}`, { done: checkbox.checked }))
    );

    const label = document.createElement("label");
    label.htmlFor = checkbox.id;
    label.textContent = task.title;

    const remove = document.createElement("button");
    remove.className = "delete";
    remove.textContent = "Delete";
    remove.addEventListener("click", () => change(() => api("DELETE", `/api/tasks/${task.id}`)));

    item.append(checkbox, label, remove);
    list.append(item);
  }
}

async function refresh() {
  render(await api("GET", "/api/tasks"));
}

// Run one change on the backend, then redraw. Shows the error if it fails.
async function change(action) {
  try {
    showError("");
    await action();
  } catch (error) {
    showError(error.message);
  }
  await refresh();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  // Clear the box straight away so the next task can be typed while this one saves.
  const title = titleInput.value;
  titleInput.value = "";
  titleInput.focus();
  await change(() => api("POST", "/api/tasks", { title }));
});

refresh().catch((error) => showError(error.message));
