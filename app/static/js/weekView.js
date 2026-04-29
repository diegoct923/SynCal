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

    const dayTasks = weekTasks
      .filter(task => task.date === dayDate)
      .map(task => {
        const startHour = Number(task.startHour ?? 9);
        const duration = Number(task.duration ?? 1);
        const endHour = Math.min(startHour + duration, 24);

        return {
          ...task,
          startHour,
          duration,
          endHour
        };
      })
      .sort((a, b) => a.startHour - b.startHour);

    const groups = [];

    dayTasks.forEach(task => {
      let placed = false;

      for (const group of groups) {
        const groupStart = Math.min(...group.map(t => t.startHour));
        const groupEnd = Math.max(...group.map(t => t.endHour));

        const overlapsGroup = task.startHour < groupEnd && task.endHour > groupStart;

        if (overlapsGroup) {
          group.push(task);
          placed = true;
          break;
        }
      }

      if (!placed) {
        groups.push([task]);
      }
    });

    groups.forEach(group => {
      const total = group.length;

      group.forEach((task, index) => {
        const taskItem = document.createElement("div");
        taskItem.classList.add("week-task-item", getPriorityClass(task.priority));
        taskItem.dataset.taskId = task.id;
        taskItem.draggable = true;

        taskItem.innerHTML = `
          <strong>${task.title}</strong>
          <span>${String(task.startHour).padStart(2, "0")}:00 - ${String(task.endHour).padStart(2, "0")}:00</span>
        `;

        taskItem.style.top = `${task.startHour * HOUR_HEIGHT}px`;
        taskItem.style.height = `${task.duration * HOUR_HEIGHT - 8}px`;

        taskItem.style.left = `calc(${index} * (100% / ${total}) + 6px)`;
        taskItem.style.width = `calc((100% / ${total}) - 12px)`;
        taskItem.style.right = "auto";

        taskItem.addEventListener("contextmenu", (e) => {
          e.preventDefault();
          e.stopPropagation();

          openTaskMenu(
            Number(e.currentTarget.dataset.taskId),
            e.clientX,
            e.clientY
          );
        });

        taskItem.addEventListener("dragstart", () => {
          draggedTaskId = Number(task.id);
        });

        taskItem.addEventListener("dragend", () => {
          draggedTaskId = null;
        });
        
        if (highlightedTaskId === task.id) {
          taskItem.classList.add("week-task-highlighted");
        }

        if (highlightedTaskId !== null) {
          setTimeout(() => {
            highlightedTaskId = null;
            renderCalendar();
          }, 3000);
        }
        column.appendChild(taskItem);
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