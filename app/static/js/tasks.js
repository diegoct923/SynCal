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

let tasks = [];
let sessions = [];

function getState() {
  return APP_STATE;
}

const TIPO_TO_PRIORITY = {
    "EXAMEN": "alta",
    "TAREA": "media",
    "PRACTICO": "baja",
    "UNKNOWN": "baja"
};

async function loadTasksFromBackend() {
  const data = await apiGetTasks(getState());
  console.log("data from backend:", data);

  tasks = data.tasks.map(task => {
      const mappedPriority = TIPO_TO_PRIORITY[task.priority] ?? "baja";
      const isCompleted = task.status === "COMPLETADA";
      return {
          id: task.id,
          date: task.date,
          title: task.title,
          priority: isCompleted ? "completada" : mappedPriority,
          previousPriority: isCompleted ? mappedPriority : null,
          startHour: Math.floor(task.startHour ?? 9),
          duration: getDurationByPriority(task.priority),
          isGroup: task.es_grupal,
          status: task.status ?? null
        };
    });
  
  sessions = (data.sessions ?? []).map(s => {
      return {
          id: s.sesion_grupo,           // identificador de grupo de sesión
          task_id: s.task_id,
          date: s.date,
          title: s.tarea_nombre,
          priority: TIPO_TO_PRIORITY[s.tarea_tipo] ?? "baja",
          previousPriority: null,
          startHour: Math.floor(s.hora_inicio),
          duration: s.hora_fin - s.hora_inicio,
          isGroup: false,
          isSession: true,              // flag para distinguirlas de tareas
          status: s.status ?? null,
          tramos: s.tramos ?? []
        };
    });
    const blocks = await apiGetBlockedSlots(getState());
    blockedTimeSlots = blocks.map(block => ({
      id: block.id,
      title: block.title ?? "Bloqueado",
      startHour: parseFloat(block.hora_inicio),
      duration: parseFloat(block.hora_fin) - parseFloat(block.hora_inicio),
      dia_semana: block.dia_semana,           // null = todos los días
      repeatEveryDay: block.dia_semana === null,
      day: block.dia_semana ?? null
    }));
  

  renderCalendar();
}

function getTasksForDate(dateString) {
  const mainTasks = tasks.filter(task => task.date === dateString);
  const sessionTasks = sessions.filter(s => s.date === dateString && s.status !== "CANCELADA");
  return [...mainTasks, ...sessionTasks];
}

function getTasksForWeek(weekDates) {
  const weekStrings = weekDates.map(d =>
    formatDate(d.getFullYear(), d.getMonth(), d.getDate())
  );

  const mainTasks = tasks.filter(task => weekStrings.includes(task.date));
  const sessionTasks = sessions.filter(s => weekStrings.includes(s.date) && s.status !== "CANCELADA");
  return [...mainTasks, ...sessionTasks];
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

  const task = tasks.find(t => t.id === taskId);
  if (!task) return;

  const oldDate = task.date;
  task.date = newDate;

  (async () => {
      try {
          await fetch(`${BASE_URL}/api/tasks/reagendar`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                  task_id: taskId,
                  deadline: `${newDate}T${String(task.startHour ?? 9).padStart(2, "0")}:00:00`,
                  state: getState()
              })
          });
          //location.reload();
      } catch(err) {
          console.error("Error al reagendar:", err);
          task.date = oldDate; // revertir si falla
          renderCalendar();
      }
  })();
}

function moveTaskToDateAndHour(taskId, newDate, newHour, force = false) {

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
          task.date = oldDate;
          task.startHour = oldHour;
          renderCalendar();
      }
  })();
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

async function createTask(title, date, startHour, priority, isGroup = false, force = false) {

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

  try {
        const result = await apiCreateTask({
            title,
            priority,
            deadline: `${date} ${String(startHour).padStart(2, "0")}:00:00`
        }, getState());

        if (result.status !== "inserted") return false;

        const taskData = result.task;
        tasks.push({
            id: taskData.id,
            date: date,
            title: taskData.title,
            priority: TIPO_TO_PRIORITY[taskData.priority] ?? "baja",
            previousPriority: null,
            startHour: startHour,
            duration: duration,
            isGroup: taskData.es_grupal ?? false
        });
        console.log("result:", result);
        renderCalendar();
        return true;

    } catch(err) {
        console.error("Error al crear tarea:", err);
        return false;
    }
}
//FIN NUEVO

// NUEVO
let blockedTimeSlots = [];

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