const HOUR_HEIGHT = 56;

function renderWeekHeader(weekDates) {
  weekDaysHeader.innerHTML = "";

  const highlighted = highlightedDate
    ? new Date(highlightedDate + "T00:00:00").toDateString()
    : null;

  weekDates.forEach((date, index) => {
    const dayHeader = document.createElement("div");
    dayHeader.classList.add("week-day-header");
    dayHeader.innerHTML = `<span class="week-day-name">${getDayNameShort(index)}</span>`;

    if (highlighted && date.toDateString() === highlighted) {
      dayHeader.classList.add("week-day-highlighted");
    }

    weekDaysHeader.appendChild(dayHeader);
  });
}

function createWeekTimeSlots(weekDates) {
  weekBoard.innerHTML = "";

  weekDates.forEach(date => {
    const fullDate = formatDate(
      date.getFullYear(),
      date.getMonth(),
      date.getDate()
    );

    const column = document.createElement("article");
    column.classList.add("week-day-column");
    column.dataset.date = fullDate;

    // Marcar el día seleccionado desde "+ tareas más"
    if (highlightedDate === fullDate) {
      column.classList.add("week-day-highlighted");
    }

    column.addEventListener("dragover", (e) => {
      e.preventDefault();
      column.classList.add("drag-over");
    });

    column.addEventListener("dragleave", () => {
      column.classList.remove("drag-over");
    });

    column.addEventListener("drop", (e) => {
      e.preventDefault();
      column.classList.remove("drag-over");

      if (draggedTaskId === null) return;

      const rect = column.getBoundingClientRect();
      const y = e.clientY - rect.top;

      let newHour = Math.floor(y / HOUR_HEIGHT);

      if (newHour < 0) newHour = 0;
      if (newHour > 23) newHour = 23;

      moveTaskToDateAndHour(draggedTaskId, fullDate, newHour);

      draggedTaskId = null;
    });

    for (let hour = 0; hour < 24; hour++) {
      const addBtn = document.createElement("button");
      addBtn.classList.add("add-task-hour-btn");
      addBtn.textContent = "+";
      addBtn.style.top = `${hour * HOUR_HEIGHT + 4}px`;

      addBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        openCreateTaskModal(fullDate, hour);
      });

      column.appendChild(addBtn);
    }

    weekBoard.appendChild(column);
  });
}

function renderWeeklyTasks(weekDates) {
  const columns = document.querySelectorAll(".week-day-column");

  const weekDateStrings = weekDates.map(date =>
    formatDate(date.getFullYear(), date.getMonth(), date.getDate())
  );

  const weekTasks = getTasksForWeek(weekDates);

  for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
    const column = columns[dayIndex];
    if (!column) continue;

    const dayDate = weekDateStrings[dayIndex];

    // ── Tareas principales ────────────────────────────────────────────────
    const dayTasks = weekTasks
      .filter(task => task.date === dayDate)
      .map(task => ({
        ...task,
        startHour: Number(task.startHour ?? 9),
        duration:  Number(task.duration ?? 1),
        endHour:   Math.min(Number(task.startHour ?? 9) + Number(task.duration ?? 1), 24),
        _tipo: "tarea"
      }))
      .sort((a, b) => a.startHour - b.startHour);

    // ── Tramos de sesiones → un item por tramo ────────────────────────────
    const daySessionItems = sesiones
      .filter(s => s.date === dayDate)
      .flatMap(sesion =>
        sesion.tramos.map((tramo, i) => ({
          id:         `s-${sesion.sesion_grupo}-${i}`,
          title:      sesion.tarea_nombre,
          tarea_tipo: sesion.tarea_tipo,
          startHour:  tramo.hora_inicio,
          duration:   tramo.hora_fin - tramo.hora_inicio,
          endHour:    tramo.hora_fin,
          esContinuacion: i > 0,
          _tipo: "sesion"
        }))
      )
      .sort((a, b) => a.startHour - b.startHour);

    // ── Unificar y agrupar por solapamiento ───────────────────────────────
    const allItems = [...dayTasks, ...daySessionItems]
      .sort((a, b) => a.startHour - b.startHour);

    const groups = [];

    allItems.forEach(item => {
      let placed = false;
      for (const group of groups) {
        const groupStart = Math.min(...group.map(t => t.startHour));
        const groupEnd   = Math.max(...group.map(t => t.endHour));
        if (item.startHour < groupEnd && item.endHour > groupStart) {
          group.push(item);
          placed = true;
          break;
        }
      }
      if (!placed) groups.push([item]);
    });

    // ── Renderizar ────────────────────────────────────────────────────────
    groups.forEach(group => {
      const total = group.length;

      group.forEach((item, index) => {
        const el = document.createElement("div");

        if (item._tipo === "tarea") {
          el.classList.add("week-task-item", getPriorityClass(item.priority, item.status));
          el.dataset.taskId = item.id;
          el.draggable = true;

          el.innerHTML = `
            <strong>${item.title}</strong>
            <span>${String(Math.floor(item.startHour)).padStart(2,"0")}:00 - ${String(Math.floor(item.endHour)).padStart(2,"0")}:00</span>
          `;

          el.addEventListener("contextmenu", (e) => {
            e.preventDefault();
            e.stopPropagation();
            openTaskMenu(Number(e.currentTarget.dataset.taskId), e.clientX, e.clientY);
          });

          el.addEventListener("dragstart", () => { draggedTaskId = Number(item.id); });
          el.addEventListener("dragend",   () => { draggedTaskId = null; });

          if (highlightedTaskId === item.id) {
            el.classList.add("week-task-highlighted");
          }

          if (highlightedTaskId !== null) {
            setTimeout(() => { highlightedTaskId = null; renderCalendar(); }, 3000);
          }

        } else {
          el.classList.add("week-task-item", getPriorityClass(item.tarea_tipo), "sesion-estudio");

          el.innerHTML = `
            <strong>📚 ${item.esContinuacion ? "↳ " : ""}${item.title}</strong>
            <span>${_fmtH(item.startHour)} - ${_fmtH(item.endHour)}</span>
          `;
        }

        el.style.top    = `${item.startHour * HOUR_HEIGHT}px`;
        el.style.height = `${item.duration * HOUR_HEIGHT - 8}px`;
        el.style.left   = `calc(${index} * (100% / ${total}) + 6px)`;
        el.style.width  = `calc((100% / ${total}) - 12px)`;
        el.style.right  = "auto";

        column.appendChild(el);
      });
    });
  }
}

function renderWeeklySummary(weekDates) {
  const weekTasks = getTasksForWeek(weekDates);

  weeklyTaskCount.textContent = weekTasks.length;
  weeklyCriticalCount.textContent = weekTasks.filter(task => task.priority === "alta").length;

  const dayNames = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];
  const loadByDay = [0, 0, 0, 0, 0, 0, 0];

  weekTasks.forEach(task => {
    const taskDate = new Date(task.date + "T00:00:00");
    const monday = weekDates[0];
    const dayIndex = Math.floor((taskDate - monday) / (1000 * 60 * 60 * 24));

    if (dayIndex >= 0 && dayIndex < 7) {
      loadByDay[dayIndex]++;
    }
  });

  const maxLoad = Math.max(...loadByDay, 1);
  weeklyLoadList.innerHTML = "";

  loadByDay.forEach((count, index) => {
    const row = document.createElement("div");
    row.classList.add("weekly-load-row");

    let barClass = "low";
    if (count >= 3) barClass = "high";
    else if (count >= 2) barClass = "medium";

    row.innerHTML = `
      <span class="weekly-load-day">${dayNames[index]}</span>
      <div class="weekly-load-bar-bg">
        <div class="weekly-load-bar ${barClass}" style="width: ${(count / maxLoad) * 100}%"></div>
      </div>
    `;

    weeklyLoadList.appendChild(row);
  });

  const criticalDays = [];
  loadByDay.forEach((count, index) => {
    if (count >= 2) {
      criticalDays.push(dayNames[index].toLowerCase());
    }
  });

  if (criticalDays.length > 0) {
    weeklyTipBox.textContent = `${criticalDays.join(" , ")} son días de mayor carga. Priorizá tu estudio con anticipación.`;
  } else {
    weeklyTipBox.textContent = "La semana está equilibrada. Mantené el ritmo de estudio.";
  }
}

function renderWeekView() {
  const weekDates = getWeekDates(currentDate);
  calendarTitle.textContent = formatShortWeekTitle(weekDates[0]);

  renderWeekHeader(weekDates);
  renderWeekHours();
  createWeekTimeSlots(weekDates);
  renderWeeklyTasks(weekDates);
  renderWeeklySummary(weekDates);
}

function renderWeekHours() {
  weekHoursColumn.innerHTML = "";

  for (let hour = 0; hour < 24; hour++) {
    const hourItem = document.createElement("div");
    hourItem.classList.add("week-hour");
    hourItem.textContent = `${String(hour).padStart(2, "0")}:00`;
    weekHoursColumn.appendChild(hourItem);
  }
}

function _fmtH(hora) {
  const h = Math.floor(hora);
  const m = Math.round((hora - h) * 60);
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}