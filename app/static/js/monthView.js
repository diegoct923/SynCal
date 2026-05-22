function createDayCell(dayNumber, fullDate, isOtherMonth = false) {
  const day = document.createElement("article");
  day.classList.add("calendar-day");
  day.dataset.date = fullDate;

  if (isToday(fullDate)) {
    day.classList.add("today");
  }


  if (isOtherMonth) {
    day.classList.add("other-month");
  }

  const number = document.createElement("span");
  number.classList.add("day-number");
  number.textContent = dayNumber;

  const taskList = document.createElement("div");
  taskList.classList.add("task-list");

  const dayTasks = getTasksForDate(fullDate);
  const visibleTasks = dayTasks.slice(0, 1);
  const hiddenCount = dayTasks.length - visibleTasks.length;

  visibleTasks.forEach(task => {
    const taskItem = document.createElement("div");
    taskItem.classList.add("task-item", getPriorityClass(task.priority));

    taskItem.innerHTML = `
      ${task.isGroup ? '<span class="group-task-icon">👥</span>' : ""}
      <span>${task.title}</span>
    `;
    //FIN NUEVO
    taskItem.draggable = true;
    taskItem.dataset.taskId = task.id;
    // taskItem.textContent = task.title;
    taskItem.draggable = true;
    taskItem.dataset.taskId = task.id;

    taskItem.addEventListener("dragstart", () => {
      draggedTaskId = Number(task.id);
    });

    taskItem.addEventListener("dragend", () => {
      draggedTaskId = null;
    });

    taskItem.addEventListener("contextmenu", (e) => {
      e.preventDefault();
      e.stopPropagation();

      openTaskMenu(
        Number(e.currentTarget.dataset.taskId),
        e.clientX,
        e.clientY
      );
    });


    if (isTouchDevice()) {
      taskItem.addEventListener("touchend", (e) => {
        e.preventDefault();
        e.stopPropagation();

        const touch = e.changedTouches[0];

        openTaskMenu(
          Number(task.id),
          touch.clientX,
          touch.clientY
        );
      }, { passive: false });
    }

    taskList.appendChild(taskItem);
  });

  if (hiddenCount > 0) {
    const moreItem = document.createElement("div");
    moreItem.classList.add("task-more-indicator");
    moreItem.textContent = `+${hiddenCount} tareas más`;

    moreItem.addEventListener("click", (e) => {
      e.stopPropagation();
      showMoreTasks(fullDate);
    });

    taskList.appendChild(moreItem);
  }

  day.addEventListener("dragover", (e) => {
    e.preventDefault();
    day.classList.add("drag-over");
  });

  day.addEventListener("dragleave", () => {
    day.classList.remove("drag-over");
  });

  day.addEventListener("drop", (e) => {
    e.preventDefault();
    day.classList.remove("drag-over");

    if (draggedTaskId === null) return;

    moveTaskToDate(draggedTaskId, fullDate);
    draggedTaskId = null;
  });

  const addTaskBtn = document.createElement("button");
  addTaskBtn.classList.add("add-task-btn");
  addTaskBtn.textContent = "+";

  addTaskBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    openCreateTaskModal(fullDate, 9);
  });

  day.appendChild(number);
  day.appendChild(addTaskBtn);
  day.appendChild(taskList);

  return day;
}
function renderMonthView() {
  monthLayout.classList.remove("hidden");
  monthWeekdays.classList.remove("hidden");
  weekViewWrapper.classList.add("hidden");
  calendarGrid.classList.remove("hidden");
  weekSummaryPanel.classList.add("hidden");

  calendarGrid.innerHTML = "";

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  calendarTitle.textContent = `${monthNames[month]} ${year}`;

  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);

  let startDay = firstDayOfMonth.getDay();
  startDay = startDay === 0 ? 6 : startDay - 1;

  const daysInMonth = lastDayOfMonth.getDate();
  const prevMonthLastDay = new Date(year, month, 0).getDate();

  for (let i = startDay; i > 0; i--) {
    const dayNumber = prevMonthLastDay - i + 1;
    const prevMonthDate = new Date(year, month - 1, dayNumber);
    const fullDate = formatDate(
      prevMonthDate.getFullYear(),
      prevMonthDate.getMonth(),
      prevMonthDate.getDate()
    );

    calendarGrid.appendChild(createDayCell(dayNumber, fullDate, true));
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const fullDate = formatDate(year, month, day);
    calendarGrid.appendChild(createDayCell(day, fullDate, false));
  }

  const totalCells = calendarGrid.children.length;
  const remainingCells = 42 - totalCells;

  for (let day = 1; day <= remainingCells; day++) {
    const nextMonthDate = new Date(year, month + 1, day);
    const fullDate = formatDate(
      nextMonthDate.getFullYear(),
      nextMonthDate.getMonth(),
      nextMonthDate.getDate()
    );

    calendarGrid.appendChild(createDayCell(day, fullDate, true));
  }
}