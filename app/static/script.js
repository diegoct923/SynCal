const calendarTitle = document.getElementById("calendarTitle");
const calendarGrid = document.getElementById("calendarGrid");
const prevMonthBtn = document.getElementById("prevMonth");
const nextMonthBtn = document.getElementById("nextMonth");
const monthViewBtn = document.getElementById("monthViewBtn");
const weekViewBtn = document.getElementById("weekViewBtn");

const monthLayout = document.getElementById("monthLayout");
const weekLayout = document.getElementById("weekLayout");
const weekDaysHeader = document.getElementById("weekDaysHeader");
const weekBoard = document.getElementById("weekBoard");
const weeklyTaskCount = document.getElementById("weeklyTaskCount");
const weeklyCriticalCount = document.getElementById("weeklyCriticalCount");
const weeklyLoadList = document.getElementById("weeklyLoadList");
const weeklyTipBox = document.getElementById("weeklyTipBox");
const monthWeekdays = document.getElementById("monthWeekdays");
const weekSummaryPanel = document.getElementById("weekSummaryPanel");
const weekViewWrapper = document.getElementById("weekViewWrapper");

const monthNames = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
];

// Datos de prueba
/*const tasks = [
  { date: "2026-04-01", title: "Prueba", priority: "baja" },
  { date: "2026-03-30", title: "Lectura Cap 2", priority: "baja" },
  { date: "2026-04-04", title: "Resumen Historia", priority: "completada" },
  { date: "2026-04-05", title: "Exposición GAL", priority: "media" },
  { date: "2026-04-05", title: "Parcial Economía", priority: "baja" },
  { date: "2026-04-08", title: "Entrega AM2", priority: "alta" },
  { date: "2026-04-08", title: "Leer Teología", priority: "baja" },
  { date: "2026-04-17", title: "Examen Infra", priority: "media" },
  { date: "2026-04-20", title: "Trabajo Grupo", priority: "media" },
  { date: "2026-04-30", title: "Examen BD", priority: "alta" },
  { date: "2026-04-30", title: "Entrega Redes", priority: "baja" }
];*/

let currentDate = new Date(2026, 3, 1); // Abril 2026
let currentView = "month";

function formatDate(year, month, day) {
  const mm = String(month + 1).padStart(2, "0");
  const dd = String(day).padStart(2, "0");
  return `${year}-${mm}-${dd}`;
}

function getTasksForDate(dateString) {
  return tasks.filter(task => task.date === dateString);
}

function getPriorityClass(priority) {
  switch (priority) {
    case "EXAMEN":
      return "prioridad-alta";
    case "TAREA":
      return "prioridad-media";
    case "PRACTICO":
      return "prioridad-baja";
    case "completada":
      return "prioridad-completada";
    default:
      return "";
  }
}

function createDayCell(dayNumber, fullDate, isOtherMonth = false) {
  const day = document.createElement("article");
  day.classList.add("calendar-day");
  if (isOtherMonth) {
    day.classList.add("other-month");
  }

  const number = document.createElement("span");
  number.classList.add("day-number");
  number.textContent = dayNumber;

  const taskList = document.createElement("div");
  taskList.classList.add("task-list");

  const dayTasks = getTasksForDate(fullDate);

  dayTasks.forEach(task => {
    const taskItem = document.createElement("div");
    taskItem.classList.add("task-item", getPriorityClass(task.priority));
    taskItem.textContent = task.title;
    taskList.appendChild(taskItem);
  });

  day.appendChild(number);
  day.appendChild(taskList);

  return day;
}

function getMondayOfWeek(date) {
  const temp = new Date(date);
  const day = temp.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  temp.setDate(temp.getDate() + diff);
  temp.setHours(0, 0, 0, 0);
  return temp;
}

function getWeekDates(baseDate) {
  const monday = getMondayOfWeek(baseDate);
  const dates = [];

  for (let i = 0; i < 7; i++) {
    const d = new Date(monday);
    d.setDate(monday.getDate() + i);
    dates.push(d);
  }

  return dates;
}

function getTasksForWeek(weekDates) {
  const weekStrings = weekDates.map(d =>
    formatDate(d.getFullYear(), d.getMonth(), d.getDate())
  );

  return tasks.filter(task => weekStrings.includes(task.date));
}

function formatShortWeekTitle(startDate) {
  const endDate = new Date(startDate);
  endDate.setDate(startDate.getDate() + 6);

  const startDay = startDate.getDate();
  const endDay = endDate.getDate();
  const endMonth = monthNames[endDate.getMonth()];

  return `Semana ${startDay} - ${endDay} ${endMonth}`;
}

function getDayNameShort(index) {
  const names = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"];
  return names[index];
}

function renderWeekHeader(weekDates) {
  weekDaysHeader.innerHTML = "";

  weekDates.forEach((date, index) => {
    const dayHeader = document.createElement("div");
    dayHeader.classList.add("week-day-header");
    dayHeader.innerHTML = `<span class="week-day-name">${getDayNameShort(index)}</span>`;
    weekDaysHeader.appendChild(dayHeader);
  });
}

function renderWeekBoard(weekDates) {
  weekBoard.innerHTML = "";

  weekDates.forEach(date => {
    const fullDate = formatDate(
      date.getFullYear(),
      date.getMonth(),
      date.getDate()
    );

    const dayTasks = getTasksForDate(fullDate);

    const dayColumn = document.createElement("article");
    dayColumn.classList.add("week-day-column");

    const dayNumber = document.createElement("div");
    dayNumber.classList.add("week-day-number");
    dayNumber.textContent = date.getDate();

    const taskList = document.createElement("div");
    taskList.classList.add("week-day-task-list");

    if (dayTasks.length === 0) {
      const emptyState = document.createElement("div");
      emptyState.classList.add("week-day-empty");
      emptyState.textContent = "Sin tareas";
      taskList.appendChild(emptyState);
    } else {
      dayTasks.forEach(task => {
        const taskItem = document.createElement("div");
        taskItem.classList.add("week-task-item", getPriorityClass(task.priority));
        taskItem.textContent = task.title;
        taskList.appendChild(taskItem);
      });
    }

    dayColumn.appendChild(dayNumber);
    dayColumn.appendChild(taskList);
    weekBoard.appendChild(dayColumn);
  });
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
    if (index > 4) return;

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
    if (count >= 2 && index <= 4) {
      criticalDays.push(dayNames[index].toLowerCase());
    }
  });

  if (criticalDays.length > 0) {
    weeklyTipBox.textContent = `${criticalDays.join(" y ")} son días de mayor carga. Priorizá tu estudio con anticipación.`;
  } else {
    weeklyTipBox.textContent = "La semana está equilibrada. Mantené el ritmo de estudio.";
  }
}

function renderWeekView() {
  const weekDates = getWeekDates(currentDate);
  calendarTitle.textContent = formatShortWeekTitle(weekDates[0]);

  renderWeekHeader(weekDates);
  renderWeekBoard(weekDates);
  renderWeeklySummary(weekDates);
}

function renderCalendar() {
  if (currentView === "month") {
    monthLayout.classList.remove("hidden");
    monthWeekdays.classList.remove("hidden");
    weekViewWrapper.classList.add("hidden");
    calendarGrid.classList.remove("hidden");

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
  } else {
    monthLayout.classList.add("hidden");
    monthWeekdays.classList.add("hidden");
    weekViewWrapper.classList.remove("hidden");

    renderWeekView();
  }
}

prevMonthBtn.addEventListener("click", () => {
  if (currentView === "month") {
    currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1);
  } else {
    currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate() - 7);
  }
  renderCalendar();
});

nextMonthBtn.addEventListener("click", () => {
  if (currentView === "month") {
    currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1);
  } else {
    currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate() + 7);
  }
  renderCalendar();
});

monthViewBtn.addEventListener("click", () => {
  currentView = "month";
  monthViewBtn.classList.add("active");
  weekViewBtn.classList.remove("active");
  calendarGrid.classList.remove("hidden");
  renderCalendar();
});

weekViewBtn.addEventListener("click", () => {
  currentView = "week";
  weekViewBtn.classList.add("active");
  monthViewBtn.classList.remove("active");
  renderCalendar();
});

renderCalendar();