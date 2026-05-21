// const tasks = [
//   {
//     id: 1,
//     date: "2026-05-01",
//     title: "Prueba",
//     priority: "baja",
//     previousPriority: null,
//     startHour: 9,
//     duration: 1,
//     isGroup: false
//   },
//   {
//     id: 2,
//     date: "2026-05-05",
//     title: "Parcial Economía",
//     priority: "alta",
//     previousPriority: null,
//     startHour: 15,
//     duration: 2,
//     isGroup: false
//   },
//   {
//     id: 3,
//     date: "2026-05-02",
//     title: "Leer Teología",
//     priority: "baja",
//     previousPriority: null,
//     startHour: 11,
//     duration: 1,
//     isGroup: false
//   },
//   {
//     id: 4,
//     date: "2026-05-03",
//     title: "Resumen Historia",
//     priority: "completada",
//     previousPriority: "media",
//     startHour: 10,
//     duration: 1,
//     isGroup: false
//   },
//   {
//     id: 5,
//     date: "2026-04-03",
//     title: "Ejercicios Álgebra",
//     priority: "media",
//     previousPriority: null,
//     startHour: 14,
//     duration: 2,
//     isGroup: false
//   },
//   {
//     id: 6,
//     date: "2026-04-04",
//     title: "Exposición GAL",
//     priority: "media",
//     previousPriority: null,
//     startHour: 9,
//     duration: 1,
//     isGroup: true
//   },
//   {
//     id: 7,
//     date: "2026-04-04",
//     title: "Repaso Economía",
//     priority: "alta",
//     previousPriority: null,
//     startHour: 16,
//     duration: 2,
//     isGroup: false
//   },
//   {
//     id: 8,
//     date: "2026-04-04",
//     title: "Ver clase grabada",
//     priority: "baja",
//     previousPriority: null,
//     startHour: 19,
//     duration: 1,
//     isGroup: false
//   },
//   {
//     id: 9,
//     date: "2026-04-05",
//     title: "Trabajo Grupo",
//     priority: "media",
//     previousPriority: null,
//     startHour: 10,
//     duration: 2,
//     isGroup: true
//   },
//   {
//     id: 10,
//     date: "2026-04-05",
//     title: "Leer Cap 3",
//     priority: "baja",
//     previousPriority: null,
//     startHour: 18,
//     duration: 1,
//     isGroup: false
//   },
//   {
//     id: 11,
//     date: "2026-04-08",
//     title: "Entrega AM2",
//     priority: "alta",
//     previousPriority: null,
//     startHour: 8,
//     duration: 2,
//     isGroup: false
//   },
//   {
//     id: 12,
//     date: "2026-04-08",
//     title: "Practicar ejercicios",
//     priority: "media",
//     previousPriority: null,
//     startHour: 13,
//     duration: 2,
//     isGroup: false
//   },
//   {
//     id: 13,
//     date: "2026-04-10",
//     title: "Revisión proyecto",
//     priority: "media",
//     previousPriority: null,
//     startHour: 17,
//     duration: 1,
//     isGroup: true
//   },
//   {
//     id: 14,
//     date: "2026-04-12",
//     title: "Simulacro parcial",
//     priority: "alta",
//     previousPriority: null,
//     startHour: 9,
//     duration: 2,
//     isGroup: false
//   },
//   {
//     id: 15,
//     date: "2026-04-12",
//     title: "Repaso apuntes",
//     priority: "media",
//     previousPriority: null,
//     startHour: 13,
//     duration: 1,
//     isGroup: false
//   },
//   {
//     id: 16,
//     date: "2026-04-12",
//     title: "Organizar notas",
//     priority: "baja",
//     previousPriority: null,
//     startHour: 19,
//     duration: 1,
//     isGroup: false
//   },
//   {
//     id: 17,
//     date: "2026-04-17",
//     title: "Examen Infra",
//     priority: "alta",
//     previousPriority: null,
//     startHour: 8,
//     duration: 2,
//     isGroup: false
//   },
//   {
//     id: 18,
//     date: "2026-04-17",
//     title: "Repaso final",
//     priority: "media",
//     previousPriority: null,
//     startHour: 14,
//     duration: 2,
//     isGroup: false
//   },
//   {
//     id: 19,
//     date: "2026-04-20",
//     title: "Trabajo Grupo",
//     priority: "media",
//     previousPriority: null,
//     startHour: 11,
//     duration: 2,
//     isGroup: true
//   },
//   {
//     id: 20,
//     date: "2026-04-20",
//     title: "Reunión equipo",
//     priority: "media",
//     previousPriority: null,
//     startHour: 16,
//     duration: 1,
//     isGroup: true
//   },
//   {
//     id: 21,
//     date: "2026-04-20",
//     title: "Ajustes finales",
//     priority: "baja",
//     previousPriority: null,
//     startHour: 20,
//     duration: 1,
//     isGroup: false
//   },
//   {
//     id: 22,
//     date: "2026-04-30",
//     title: "Examen BD",
//     priority: "alta",
//     previousPriority: null,
//     startHour: 9,
//     duration: 2,
//     isGroup: false
//   },
//   {
//     id: 23,
//     date: "2026-04-30",
//     title: "Entrega Redes",
//     priority: "media",
//     previousPriority: null,
//     startHour: 13,
//     duration: 1,
//     isGroup: true
//   },
//   {
//     id: 24,
//     date: "2026-04-30",
//     title: "Repaso consultas",
//     priority: "baja",
//     previousPriority: null,
//     startHour: 16,
//     duration: 1,
//     isGroup: false
//   },
//   {
//     id: 25,
//     date: "2026-04-30",
//     title: "Organizar apuntes",
//     priority: "baja",
//     previousPriority: null,
//     startHour: 19,
//     duration: 1,
//     isGroup: false
//   }
// ];

async function loadTasksFromBackend() {
  // FETCH: traer todas las tareas desde Python (/tasks)
}

function getTasksForDate(dateString) {
  return tasks.filter(task => task.date === dateString);
}

function getTasksForWeek(weekDates) {
  const weekStrings = weekDates.map(d =>
    formatDate(d.getFullYear(), d.getMonth(), d.getDate())
  );

  return tasks.filter(task => weekStrings.includes(task.date));
}

function getPriorityClass(priority) {
  switch (priority) {
    case "alta":
      return "prioridad-alta";
    case "media":
      return "prioridad-media";
    case "baja":
      return "prioridad-baja";
    case "completada":
      return "prioridad-completada";
    default:
      return "";
  }
}

function moveTaskToDate(taskId, newDate) {

  // FETCH: PUT → actualizar fecha de la tarea

  const task = tasks.find(t => t.id === taskId);
  if (!task) return;

  task.date = newDate;
  renderCalendar();
}

function moveTaskToDateAndHour(taskId, newDate, newHour, force = false) {

    // FETCH: PUT → actualizar fecha + hora

  const task = tasks.find(t => t.id === taskId);
  if (!task) return;

  const oldDate = task.date;
  const oldHour = task.startHour;

  const duration = Number(task.duration ?? 1);
  const dayIndex = getDayIndexFromDate(newDate);

  const conflict = getBlockedSlotConflict(dayIndex, newHour, duration);

  if (conflict && !force) {
    openConfirmBlockedSlotModal(
      () => {
        moveTaskToDateAndHour(taskId, newDate, newHour, true);
      },
      () => {
        task.date = oldDate;
        task.startHour = oldHour;
        renderCalendar();
      },
      conflict
    );

    return;
  }

  task.date = newDate;
  task.startHour = Number(newHour);

  renderCalendar();
}


function getNextTaskId() {
  if (tasks.length === 0) return 1;
  return Math.max(...tasks.map(task => task.id)) + 1;
}

function getDurationByPriority(priority) {
  switch (priority) {
    case "alta":
      return 3;
    case "media":
      return 2;
    case "baja":
      return 1;
    default:
      return 1;
  }
}

function createTask(title, date, startHour, priority, isGroup = false, force = false) {

    // FETCH: POST → crear nueva tarea

  const duration = getDurationByPriority(priority);
  const dayIndex = getDayIndexFromDate(date);

  const conflict = getBlockedSlotConflict(dayIndex, startHour, duration);

  if (conflict && !force) {
    openConfirmBlockedSlotModal(
      () => {
        createTask(title, date, startHour, priority, isGroup, true);
      },
      () => {
        renderCalendar();
      },
      conflict
    );

    return false;
  }

  const newTask = {
    id: getNextTaskId(),
    date: date,
    title: title,
    priority: priority,
    previousPriority: null,
    startHour: Number(startHour),
    duration: duration,
    isGroup: isGroup
  };

  tasks.push(newTask);
  renderCalendar();

  return true;
}
//FIN NUEVO

// NUEVO
const blockedTimeSlots = [
  {
    id: 1,
    title: "Sueño",
    startHour: 0,
    duration: 8,
    repeatEveryDay: true
  },
  {
    id: 2,
    title: "Almuerzo",
    startHour: 12,
    duration: 1,
    repeatEveryDay: true
  },
  {
    id: 3,
    title: "Cena",
    startHour: 21,
    duration: 1,
    repeatEveryDay: true
  }
];

function getNextBlockedSlotId() {
  if (blockedTimeSlots.length === 0) return 1;
  return Math.max(...blockedTimeSlots.map(slot => slot.id)) + 1;
}

function createBlockedSlot(day, startHour, duration, title) {

  // FETCH: POST → crear franja bloqueada

  blockedTimeSlots.push({
    id: getNextBlockedSlotId(),
    title: title || "Bloqueado",
    day: Number(day),
    startHour: Number(startHour),
    duration: Number(duration),
    repeatEveryDay: false
  });

  renderCalendar();
}

function deleteBlockedSlot(slotId) {

  // FETCH: DELETE → eliminar franja bloqueada, no definido aun

  const index = blockedTimeSlots.findIndex(slot => slot.id === slotId);

  if (index !== -1) {
    blockedTimeSlots.splice(index, 1);
    renderCalendar();
    openBlockedSlotsModal();
  }
}

function getBlockedSlotConflict(dayIndex, startHour, duration) {
  const taskStart = Number(startHour);
  const taskEnd = taskStart + Number(duration);

  return blockedTimeSlots.find(block => {
    const blockStart = Number(block.startHour);
    const blockEnd = blockStart + Number(block.duration);

    if (block.repeatEveryDay) {
      return taskStart < blockEnd && taskEnd > blockStart;
    }

    if (Number(block.day) !== Number(dayIndex)) {
      return false;
    }

    return taskStart < blockEnd && taskEnd > blockStart;
  });
}

function getDayIndexFromDate(dateString) {
  const date = new Date(dateString + "T00:00:00");
  const day = date.getDay();

  return day === 0 ? 6 : day - 1;
}
// FIN NUEVO