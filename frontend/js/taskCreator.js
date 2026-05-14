function openCreateTaskModal(defaultDate, defaultHour = 9) {
  //REEMPLAZAR
  openCustomModal(
    "Crear tarea",
    `
      <label for="newTaskTitle">Nombre de la tarea</label>
      <input id="newTaskTitle" type="text" placeholder="Ej: Parcial de matemática">

      <label for="newTaskDate">Día</label>
      <input id="newTaskDate" type="date" value="${defaultDate}">

      <label for="newTaskHour">Hora de inicio</label>
      <input id="newTaskHour" type="number" min="0" max="23" value="${defaultHour}">

      <label for="newTaskPriority">Prioridad</label>
      <select id="newTaskPriority">
        <option value="alta">Alta - 3 horas</option>
        <option value="media" selected>Media - 2 horas</option>
        <option value="baja">Baja - 1 hora</option>
      </select>

      <label for="newTaskType">Tipo de tarea</label>
      <select id="newTaskType">
        <option value="individual">Individual</option>
        <option value="group">Grupal</option>
      </select>

      <div class="custom-modal-message" id="newTaskError"></div>
    `,
    //FIN REEMPLAZAR
    () => {
      const titleInput = document.getElementById("newTaskTitle");
      const dateInput = document.getElementById("newTaskDate");
      const hourInput = document.getElementById("newTaskHour");
      const priorityInput = document.getElementById("newTaskPriority");
      const error = document.getElementById("newTaskError");
      // NUEVO
      const typeInput = document.getElementById("newTaskType");
      const isGroup = typeInput.value === "group";
      // FIN NUEVO
      const title = titleInput.value.trim();
      const date = dateInput.value;
      const hour = Number(hourInput.value);
      const priority = priorityInput.value;

      if (!title) {
        error.textContent = "El nombre de la tarea no puede estar vacío.";
        return;
      }

      if (!date) {
        error.textContent = "Tenés que seleccionar un día.";
        return;
      }

      if (Number.isNaN(hour) || hour < 0 || hour > 23) {
        error.textContent = "La hora debe estar entre 0 y 23.";
        return;
      }

      const duration = getDurationByPriority(priority);

      if (hour + duration > 24) {
        error.textContent = "La tarea no puede terminar después de las 24:00.";
        return;
      }

      // ELIMINAR
      //createTask(title, date, hour, priority);
      // closeCustomModal();
      // FIN ELIMINAR

      //NUEVO
      const wasCreated = createTask(title, date, hour, priority, isGroup);

      if (wasCreated) {
        closeCustomModal();
      }
      //FIN NUEVO
    },
    "Crear tarea"
  );
}