function openTaskMenu(taskId, x, y) {
  const task = tasks.find(t => t.id === taskId);
  if (!task) return;

  selectedTaskId = taskId;

  if (task.priority === "completada") {
    completeTaskBtn.textContent = "Marcar como no completada";
  } else {
    completeTaskBtn.textContent = "Marcar como completada";
  }

  if (currentView === "week") {
    viewTaskWeekBtn.classList.add("hidden");
  } else {
    viewTaskWeekBtn.classList.remove("hidden");
  }

  taskMenu.classList.remove("hidden");

  const menuWidth = taskMenu.offsetWidth;
  const menuHeight = taskMenu.offsetHeight;

  const windowWidth = window.innerWidth;
  const windowHeight = window.innerHeight;

  let posX = x;
  let posY = y;

  if (x + menuWidth > windowWidth) {
    posX = windowWidth - menuWidth - 10;
  }

  if (y + menuHeight > windowHeight) {
    posY = windowHeight - menuHeight - 10;
  }

  if (posX < 10) posX = 10;
  if (posY < 10) posY = 10;

    taskMenu.style.left = `${posX}px`;
    taskMenu.style.top = `${posY}px`;
}

function closeTaskMenu() {
  taskMenu.classList.add("hidden");
  selectedTaskId = null;
}

editTaskBtn.addEventListener("click", () => {
  if (selectedTaskId === null) return;

  const taskId = selectedTaskId;
  const task = tasks.find(t => t.id === taskId);
  if (!task) return;

  closeTaskMenu();

  openCustomModal(
    "Cambiar nombre",
    `
      <label for="taskTitleInput">Nombre de la tarea</label>
      <input id="taskTitleInput" type="text" value="${task.title}">
      <div class="custom-modal-message" id="taskTitleError"></div>
    `,
    () => {
      const input = document.getElementById("taskTitleInput");
      const error = document.getElementById("taskTitleError");
      const value = input.value.trim();

      if (!value) {
        error.textContent = "El nombre no puede estar vacío.";
        return;
      }

      task.title = value;
      renderCalendar();
      closeCustomModal();
    }
  );
});

changeDateTaskBtn.addEventListener("click", () => {
  if (selectedTaskId === null) return;

  const taskId = selectedTaskId;
  const task = tasks.find(t => t.id === taskId);
  if (!task) return;

  closeTaskMenu();

  openCustomModal(
    "Mover tarea",
    `
      <label for="taskDateInput">Nueva fecha</label>
      <input id="taskDateInput" type="date" value="${task.date}">

      <label for="taskHourInput">Hora de inicio</label>
      <input id="taskHourInput" type="number" min="0" max="23" value="${task.startHour ?? 9}">

      <label for="taskDurationInput">Duración estimada (horas)</label>
      <input id="taskDurationInput" type="number" min="1" max="24" value="${task.duration ?? 1}">

      <div class="custom-modal-message" id="taskMoveError"></div>
    `,
    () => {
      const dateInput = document.getElementById("taskDateInput");
      const hourInput = document.getElementById("taskHourInput");
      const durationInput = document.getElementById("taskDurationInput");
      const error = document.getElementById("taskMoveError");

      const newDate = dateInput.value;
      const newHour = Number(hourInput.value);
      const newDuration = Number(durationInput.value);

      if (!newDate) {
        error.textContent = "Tenés que seleccionar una fecha.";
        return;
      }

      if (Number.isNaN(newHour) || newHour < 0 || newHour > 23) {
        error.textContent = "La hora debe estar entre 0 y 23.";
        return;
      }

      if (Number.isNaN(newDuration) || newDuration < 1 || newDuration > 24) {
        error.textContent = "La duración debe estar entre 1 y 24 horas.";
        return;
      }

      if (newHour + newDuration > 24) {
        error.textContent = "La tarea no puede terminar después de las 24:00.";
        return;
      }

      task.date = newDate;
      task.startHour = newHour;
      task.duration = newDuration;

      renderCalendar();
      closeCustomModal();
    }
  );
});

changePriorityTaskBtn.addEventListener("click", () => {
  if (selectedTaskId === null) return;

  const taskId = selectedTaskId;
  const task = tasks.find(t => t.id === taskId);
  if (!task) return;

  closeTaskMenu();

  openCustomModal(
    "Cambiar prioridad",
    `
      <label for="taskPrioritySelect">Prioridad</label>
      <select id="taskPrioritySelect">
        <option value="alta" ${task.priority === "alta" ? "selected" : ""}>Alta</option>
        <option value="media" ${task.priority === "media" ? "selected" : ""}>Media</option>
        <option value="baja" ${task.priority === "baja" ? "selected" : ""}>Baja</option>
        <option value="completada" ${task.priority === "completada" ? "selected" : ""}>Completada</option>
      </select>
    `,
    () => {
      const select = document.getElementById("taskPrioritySelect");
      const value = select.value;

      if (value === "completada" && task.priority !== "completada") {
        task.previousPriority = task.priority;
      }

      if (value !== "completada" && task.priority === "completada") {
        task.previousPriority = null;
      }

      task.priority = value;
      renderCalendar();
      closeCustomModal();
    }
  );
});

completeTaskBtn.addEventListener("click", () => {
  if (selectedTaskId === null) return;

  const task = tasks.find(t => t.id === selectedTaskId);
  if (!task) return;

  if (task.priority === "completada") {
    task.priority = task.previousPriority || "media";
    task.previousPriority = null;
  } else {
    task.previousPriority = task.priority;
    task.priority = "completada";
  }

  renderCalendar();
  closeTaskMenu();
});

deleteTaskBtn.addEventListener("click", () => {
  if (selectedTaskId === null) return;

  const taskIdToDelete = selectedTaskId;

  closeTaskMenu();

  openCustomModal(
    "Eliminar tarea",
    `
      <p>¿Seguro que querés eliminar esta tarea?</p>
      <p class="custom-modal-message">Esta acción no se puede deshacer.</p>
    `,
    () => {
      const index = tasks.findIndex(t => t.id === taskIdToDelete);

      if (index !== -1) {
        tasks.splice(index, 1);
        renderCalendar();
      }

      closeCustomModal();
    },
    "Eliminar",
    true
  );
});

document.addEventListener("click", (e) => {
  if (!taskMenu.contains(e.target)) {
    closeTaskMenu();
  }
});

viewTaskWeekBtn.addEventListener("click", () => {
  if (selectedTaskId === null) return;

  const task = tasks.find(t => t.id === selectedTaskId);
  if (!task) return;

  highlightedDate = task.date;
  highlightedTaskId = task.id;
  currentDate = new Date(task.date + "T00:00:00");
  currentView = "week";

  weekViewBtn.classList.add("active");
  monthViewBtn.classList.remove("active");

  closeTaskMenu();
  renderCalendar();
});