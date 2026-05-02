/**const tasks = [
  {
    id: 1,
    date: "2026-04-01",
    title: "Prueba",
    priority: "baja",
    previousPriority: null,
    startHour: 9,
    duration: 1
  },
  {
    id: 2,
    date: "2026-04-05",
    title: "Parcial Economía",
    priority: "alta",
    previousPriority: null,
    startHour: 15,
    duration: 2
  },
  {
    id: 3,
    date: "2026-04-02",
    title: "Leer Teología",
    priority: "baja",
    previousPriority: null,
    startHour: 11,
    duration: 1
  },
  {
    id: 4,
    date: "2026-04-03",
    title: "Resumen Historia",
    priority: "completada",
    previousPriority: "media",
    startHour: 10,
    duration: 1
  },
  {
    id: 5,
    date: "2026-04-03",
    title: "Ejercicios Álgebra",
    priority: "media",
    previousPriority: null,
    startHour: 14,
    duration: 2
  },
  {
    id: 6,
    date: "2026-04-04",
    title: "Exposición GAL",
    priority: "media",
    previousPriority: null,
    startHour: 9,
    duration: 1
  },
  {
    id: 7,
    date: "2026-04-04",
    title: "Repaso Economía",
    priority: "alta",
    previousPriority: null,
    startHour: 16,
    duration: 2
  },
  {
    id: 8,
    date: "2026-04-04",
    title: "Ver clase grabada",
    priority: "baja",
    previousPriority: null,
    startHour: 19,
    duration: 1
  },
  {
    id: 9,
    date: "2026-04-05",
    title: "Trabajo Grupo",
    priority: "media",
    previousPriority: null,
    startHour: 10,
    duration: 2
  },
  {
    id: 10,
    date: "2026-04-05",
    title: "Leer Cap 3",
    priority: "baja",
    previousPriority: null,
    startHour: 18,
    duration: 1
  },
  {
    id: 11,
    date: "2026-04-08",
    title: "Entrega AM2",
    priority: "alta",
    previousPriority: null,
    startHour: 8,
    duration: 2
  },
  {
    id: 12,
    date: "2026-04-08",
    title: "Practicar ejercicios",
    priority: "media",
    previousPriority: null,
    startHour: 13,
    duration: 2
  },
  {
    id: 13,
    date: "2026-04-10",
    title: "Revisión proyecto",
    priority: "media",
    previousPriority: null,
    startHour: 17,
    duration: 1
  },
  {
    id: 14,
    date: "2026-04-12",
    title: "Simulacro parcial",
    priority: "alta",
    previousPriority: null,
    startHour: 9,
    duration: 2
  },
  {
    id: 15,
    date: "2026-04-12",
    title: "Repaso apuntes",
    priority: "media",
    previousPriority: null,
    startHour: 13,
    duration: 1
  },
  {
    id: 16,
    date: "2026-04-12",
    title: "Organizar notas",
    priority: "baja",
    previousPriority: null,
    startHour: 19,
    duration: 1
  },
  {
    id: 17,
    date: "2026-04-17",
    title: "Examen Infra",
    priority: "alta",
    previousPriority: null,
    startHour: 8,
    duration: 2
  },
  {
    id: 18,
    date: "2026-04-17",
    title: "Repaso final",
    priority: "media",
    previousPriority: null,
    startHour: 14,
    duration: 2
  },
  {
    id: 19,
    date: "2026-04-20",
    title: "Trabajo Grupo",
    priority: "media",
    previousPriority: null,
    startHour: 11,
    duration: 2
  },
  {
    id: 20,
    date: "2026-04-20",
    title: "Reunión equipo",
    priority: "media",
    previousPriority: null,
    startHour: 16,
    duration: 1
  },
  {
    id: 21,
    date: "2026-04-20",
    title: "Ajustes finales",
    priority: "baja",
    previousPriority: null,
    startHour: 20,
    duration: 1
  },
  {
    id: 22,
    date: "2026-04-30",
    title: "Examen BD",
    priority: "alta",
    previousPriority: null,
    startHour: 9,
    duration: 2
  },
  {
    id: 23,
    date: "2026-04-30",
    title: "Entrega Redes",
    priority: "media",
    previousPriority: null,
    startHour: 13,
    duration: 1
  },
  {
    id: 24,
    date: "2026-04-30",
    title: "Repaso consultas",
    priority: "baja",
    previousPriority: null,
    startHour: 16,
    duration: 1
  },
  {
    id: 25,
    date: "2026-04-30",
    title: "Organizar apuntes",
    priority: "baja",
    previousPriority: null,
    startHour: 19,
    duration: 1
  }
];
*/
const urlParams = new URLSearchParams(window.location.search);
const state = urlParams.get('state')

function getTasksForDate(dateString) {
  return tasks.filter(task => task.date === dateString);
}

function getTasksForWeek(weekDates) {
  const weekStrings = weekDates.map(d =>
    formatDate(d.getFullYear(), d.getMonth(), d.getDate())
  );

  return tasks.filter(task => weekStrings.includes(task.date));
}

function getPriorityClass(priority, status) {
  if(status == "COMPLETADA") return "prioridad-completada"
  switch (priority?.toUpperCase()) {
    case "EXAMEN":
      return "prioridad-alta";
    case "TAREA":
      return "prioridad-media";
    case "PRACTICO":
      return "prioridad-baja";
    case "UNKNOWN":
    default:
      return "prioridad-baja";
  }
}

function moveTaskToDate(taskId, newDate) {
  const task = tasks.find(t => t.id === taskId);
  if (!task) return;

  task.date = newDate;

  fetch('/reagendar_tarea', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task_id: taskId, deadline: newDate, state: state })
  }).catch(err => console.error('Error al reagendar:', err));

  renderCalendar();
}

function moveTaskToDateAndHour(taskId, newDate, newHour) {
  const task = tasks.find(t => t.id === taskId);
  if (!task) return;

  task.date = newDate;
  task.startHour = newHour;

  fetch('/reagendar_tarea', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task_id: taskId, deadline: `${newDate}T${String(newHour).padStart(2, "0")}:00:00`, state: state})
  }).then(() => {
    location.reload();
  }).catch(err => console.error('Error al reagendar:', err));

  renderCalendar();
}

function getNextTaskId() {
  if (tasks.length === 0) return 1;
  return Math.max(...tasks.map(task => task.id)) + 1;
}

function getDurationByPriority(priority) {
  switch (priority?.toUpperCase()) {
    case "EXAMEN":
      return 3;
    case "TAREA":
      return 2;
    case "PRACTICO":
      return 1;
    default:
      return 1;
  }
}

function createTask(title, date, startHour, priority) {
  const newTask = {
    id: getNextTaskId(),
    date: date,
    title: title,
    priority: priority,
    previousPriority: null,
    startHour: Number(startHour),
    duration: getDurationByPriority(priority)
  };

  tasks.push(newTask);
  renderCalendar();
}

// Sesiones de estudio (subtareas generadas por el scheduler)
// Inyectadas desde Flask igual que `tasks`
function getSessionsForWeek(weekDates) {
  const weekStrings = weekDates.map(d =>
    formatDate(d.getFullYear(), d.getMonth(), d.getDate())
  );
  return sesiones.filter(s => weekStrings.includes(s.date));
}

function getSessionsForDate(dateString) {
  return sesiones.filter(s => s.fecha === dateString);
}