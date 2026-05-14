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

const taskMenu = document.getElementById("taskMenu");
const editTaskBtn = document.getElementById("editTaskBtn");
const changeDateTaskBtn = document.getElementById("changeDateTaskBtn");
const changePriorityTaskBtn = document.getElementById("changePriorityTaskBtn");
const completeTaskBtn = document.getElementById("completeTaskBtn");
const deleteTaskBtn = document.getElementById("deleteTaskBtn");

const customModalOverlay = document.getElementById("customModalOverlay");
const customModalTitle = document.getElementById("customModalTitle");
const customModalBody = document.getElementById("customModalBody");
const customModalSave = document.getElementById("customModalSave");
const customModalCancel = document.getElementById("customModalCancel");
const customModalClose = document.getElementById("customModalClose");

const weekHoursColumn = document.getElementById("weekHoursColumn");
const weekDetailsBtn = document.getElementById("weekDetailsBtn");
const summaryCloseBtn = document.getElementById("summaryCloseBtn");

const viewTaskWeekBtn = document.getElementById("viewTaskWeekBtn");
const weekBoardScroll = document.getElementById("weekBoardScroll");
const weekDaysHeaderScroll = document.getElementById("weekDaysHeaderScroll");
const weekHoursScroll = document.getElementById("weekHoursScroll");

// NUEVO
const taskMenuTitle = document.getElementById("taskMenuTitle");
const taskMenuCloseBtn = document.getElementById("taskMenuCloseBtn");

const calendarOptionsBtn = document.getElementById("calendarOptionsBtn");
const calendarOptionsPanel = document.getElementById("calendarOptionsPanel");

const calendarTitleBtn = document.getElementById("calendarTitleBtn");
const monthYearPicker = document.getElementById("monthYearPicker");
const monthSelect = document.getElementById("monthSelect");
const yearSelect = document.getElementById("yearSelect");
const applyMonthYearBtn = document.getElementById("applyMonthYearBtn");

const manageBlocksBtn = document.getElementById("manageBlocksBtn");
const toggleGroupTaskBtn = document.getElementById("toggleGroupTaskBtn");
// FIN NUEVO

let highlightedTaskId = null;

//ELIMINAR
// let currentDate = new Date(2026, 3, 1); // Abril 2026
//FIN ELIMINAR

//NUEVO
const today = new Date();
let currentDate = new Date(today.getFullYear(), today.getMonth(), 1);
//FIN NUEVO

let currentView = "month";

let selectedTaskId = null;
let draggedTaskId = null;
let highlightedDate = null;

if (weekBoardScroll && weekDaysHeaderScroll && weekHoursScroll) {
  weekBoardScroll.addEventListener("scroll", () => {
    weekDaysHeaderScroll.scrollLeft = weekBoardScroll.scrollLeft;
    weekHoursScroll.scrollTop = weekBoardScroll.scrollTop;
  });
}

function renderCalendar() {
  if (currentView === "month") {
    renderMonthView();
    weekDetailsBtn.classList.add("hidden");
    weekSummaryPanel.classList.add("hidden");
    manageBlocksBtn.classList.add("hidden");
  } else {
    monthLayout.classList.add("hidden");
    monthWeekdays.classList.add("hidden");
    weekViewWrapper.classList.remove("hidden");

    weekDetailsBtn.classList.remove("hidden");
    manageBlocksBtn.classList.remove("hidden");
    weekSummaryPanel.classList.add("hidden");

    renderWeekView();
  }
}

function showMoreTasks(date) {
  highlightedDate = date;
  currentDate = new Date(date + "T00:00:00");
  currentView = "week";

  weekViewBtn.classList.add("active");
  monthViewBtn.classList.remove("active");

  renderCalendar();
}

prevMonthBtn.addEventListener("click", () => {
  if (currentView === "month") {
    currentDate = new Date(
      currentDate.getFullYear(),
      currentDate.getMonth() - 1,
      1
    );
  } else {
    currentDate = new Date(
      currentDate.getFullYear(),
      currentDate.getMonth(),
      currentDate.getDate() - 7
    );
  }

  renderCalendar();
});

nextMonthBtn.addEventListener("click", () => {
  if (currentView === "month") {
    currentDate = new Date(
      currentDate.getFullYear(),
      currentDate.getMonth() + 1,
      1
    );
  } else {
    currentDate = new Date(
      currentDate.getFullYear(),
      currentDate.getMonth(),
      currentDate.getDate() + 7
    );
  }

  renderCalendar();
});

monthViewBtn.addEventListener("click", () => {
  currentView = "month";
  highlightedDate = null;

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

weekDetailsBtn.addEventListener("click", () => {
  weekSummaryPanel.classList.remove("hidden");
});

summaryCloseBtn.addEventListener("click", () => {
  weekSummaryPanel.classList.add("hidden");
});

// NUEVO
calendarOptionsBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  calendarOptionsPanel.classList.toggle("hidden");
});

calendarOptionsPanel.addEventListener("click", (e) => {
  e.stopPropagation();
});

document.addEventListener("click", () => {
  calendarOptionsPanel.classList.add("hidden");
});

calendarTitleBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  datePickerMenu.classList.toggle("hidden");
});

function loadYearOptions() {
  yearSelect.innerHTML = "";

  const currentYear = new Date().getFullYear();

  for (let year = currentYear - 5; year <= currentYear + 10; year++) {
    const option = document.createElement("option");
    option.value = year;
    option.textContent = year;
    yearSelect.appendChild(option);
  }
}

calendarTitleBtn.addEventListener("click", (e) => {
  e.stopPropagation();

  monthSelect.value = currentDate.getMonth();
  yearSelect.value = currentDate.getFullYear();

  monthYearPicker.classList.toggle("hidden");
});

applyMonthYearBtn.addEventListener("click", (e) => {
  e.stopPropagation();

  const selectedMonth = Number(monthSelect.value);
  const selectedYear = Number(yearSelect.value);

  if (currentView === "month") {
    currentDate = new Date(selectedYear, selectedMonth, 1);
  } else {
    currentDate = new Date(selectedYear, selectedMonth, 1);
  }

  monthYearPicker.classList.add("hidden");
  renderCalendar();
});

monthYearPicker.addEventListener("click", (e) => {
  e.stopPropagation();
});

document.addEventListener("click", () => {
  monthYearPicker.classList.add("hidden");
});

loadYearOptions();
// FIN NUEVO

renderCalendar();