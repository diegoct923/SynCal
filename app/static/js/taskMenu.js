function openTaskMenu(taskId, x, y) {
  const task = tasks.find(t => t.id === taskId);
  if (!task) return;

  selectedTaskId = taskId;
  taskMenuTitle.textContent = task.title;

  completeTaskBtn.textContent =
    task.priority === "completada"
      ? "Marcar como no completada"
      : "Marcar como completada";

  toggleGroupTaskBtn.textContent = task.isGroup
    ? "Cambiar a individual"
    : "Cambiar a grupal";


  if (currentView === "week") {
    viewTaskWeekBtn.classList.add("hidden");
  } else {
    viewTaskWeekBtn.classList.remove("hidden");
  }

  taskMenu.classList.remove("hidden");

  if (isTouchDevice()) {
    taskMenu.classList.add("task-menu-touch");
    taskMenu.style.left = "50%";
    taskMenu.style.top = "50%";
    taskMenu.style.transform = "translate(-50%, -50%)";

    taskMenu.style.pointerEvents = "none";

    setTimeout(() => {
      taskMenu.style.pointerEvents = "auto";
    }, 50);

    return;
  }

  taskMenu.classList.remove("task-menu-touch");
  taskMenu.style.transform = "none";

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
  taskMenu.classList.remove("task-menu-touch");
  taskMenu.style.left = "";
  taskMenu.style.top = "";
  taskMenu.style.transform = "";
  taskMenu.style.pointerEvents = "";
  selectedTaskId = null;
}

taskMenuCloseBtn.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();
  closeTaskMenu();
});

taskMenu.addEventListener("click", (e) => {
  e.stopPropagation();
});

taskMenu.addEventListener("touchstart", (e) => {
  e.stopPropagation();
}, { passive: true });

document.addEventListener("click", (e) => {
  if (!taskMenu.classList.contains("hidden") && !taskMenu.contains(e.target)) {
    closeTaskMenu();
  }
});


editTaskBtn.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();

  if (selectedTaskId === null) return;

  const taskId = selectedTaskId;
  const task = tasks.find(t => t.id === taskId);
  if (!task) return;

  closeTaskMenu();

  openCustomModal(
    "Editar tarea",
    `
      <label for="taskTitleInput">Nombre de la tarea</label>
      <input id="taskTitleInput" type="text" value="${task.title}">

      <label for="taskTypeSelect">Tipo de tarea</label>
      <select id="taskTypeSelect">
        <option value="individual" ${!task.isGroup ? "selected" : ""}>Individual</option>
        <option value="group" ${task.isGroup ? "selected" : ""}>Grupal</option>
      </select>

      <div class="custom-modal-message" id="taskTitleError"></div>
    `,
    async () => {
      const input = document.getElementById("taskTitleInput");
      const typeSelect = document.getElementById("taskTypeSelect");
      const error = document.getElementById("taskTitleError");

      const value = input.value.trim();

      if (!value) {
        error.textContent = "El nombre no puede estar vacío.";
        return;
      }

      task.title = value;
      task.isGroup = typeSelect.value === "group";
      closeCustomModal()
      try {
          await fetch(`${BASE_URL}/api/tasks/nombre`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                  task_id: taskId,
                  title: value,
                  state: getState()
              })
          });
          //location.reload();
      } catch(err) {
          console.error("Error al actualizar nombre:", err);
      }       
    }
  );
});

changeDateTaskBtn.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();
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

      closeCustomModal();

      (async () => {
          try {
              await fetch(`${BASE_URL}/api/tasks/reagendar`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                      task_id: taskId,
                      deadline: `${newDate}T${String(newHour).padStart(2, "0")}:00:00`,
                      state: getState()
                  })
              });
              //location.reload();
          } catch(err) {
              console.error("Error al reagendar:", err);
          }
      })(); 

      closeCustomModal();
    }
  );
});

changePriorityTaskBtn.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();
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
    async () => {
      const select = document.getElementById("taskPrioritySelect");
      const value = select.value;

      if (value === "completada" && task.priority !== "completada") {
        task.previousPriority = task.priority;
      }

      if (value !== "completada" && task.priority === "completada") {
        task.previousPriority = null;
      }

      task.priority = value;

      closeCustomModal();

      try {
          await fetch(`${BASE_URL}/api/tasks/prioridad`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                  task_id: taskId,
                  priority: value,
                  state: getState()
              })
          });
          //location.reload();
      } catch(err) {
          console.error("Error al actualizar prioridad:", err);
      }
      closeCustomModal();
    }
  );
});

completeTaskBtn.addEventListener("click", async (e) => {
  e.preventDefault();
  e.stopPropagation();
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

  try {
    await fetch(`${BASE_URL}/api/tasks/complete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        state: getState(),
        task_id: task.id
      })
    });
    //location.reload();
  } catch(err) {
    console.error("Error al completar:", err);
  }

});

deleteTaskBtn.addEventListener("click", (e) => {
  if (selectedTaskId === null) return;

  const taskIdToDelete = selectedTaskId;

  closeTaskMenu();

  openCustomModal(
    "Eliminar tarea",
    `
      <p>¿Seguro que querés eliminar esta tarea?</p>
      <p class="custom-modal-message">Esta acción no se puede deshacer.</p>
    `,
    async () => {
      const index = tasks.findIndex(t => t.id === taskIdToDelete);

      if (index !== -1) {
          tasks.splice(index, 1);
          try {
            await fetch(`${BASE_URL}/api/tasks/delete`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    task_id: taskIdToDelete,
                    state: getState()
                })
            });
            //location.reload();
        } catch(err) {
          console.error("Error al borrar:", err);
        }
        
      }

      closeCustomModal();
    },
    "Eliminar",
    true
  );
});

viewTaskWeekBtn.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();
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

toggleGroupTaskBtn.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();

  if (selectedTaskId === null) return;

  const task = tasks.find(t => t.id === selectedTaskId);
  if (!task) return;

  task.isGroup = !task.isGroup;

  // FETCH: actualizar tipo grupal/individual

  renderCalendar();
  closeTaskMenu();
});