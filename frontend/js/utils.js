const monthNames = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
];

// NUEVO
function isTouchDevice() {
  return (
    "ontouchstart" in window ||
    navigator.maxTouchPoints > 0
  );
}
// FIN NUEVO

function addTaskInteractionHandlers(taskItem, taskId) {
  const openMenu = (x, y) => {
    openTaskMenu(taskId, x, y);
  };

  taskItem.addEventListener("contextmenu", (e) => {
    e.preventDefault();
    e.stopPropagation();
    openMenu(e.clientX, e.clientY);
  });

  if (isTouchDevice()) {
    let pressTimer = null;
    let startX = 0;
    let startY = 0;
    let didMove = false;

    taskItem.addEventListener("touchstart", (e) => {
      const touch = e.touches[0];

      startX = touch.clientX;
      startY = touch.clientY;
      didMove = false;

      pressTimer = setTimeout(() => {
        if (!didMove) {
          e.preventDefault();
          openMenu(touch.clientX, touch.clientY);
        }
      }, 650);
    }, { passive: false });

    taskItem.addEventListener("touchmove", (e) => {
      const touch = e.touches[0];

      const distanceX = Math.abs(touch.clientX - startX);
      const distanceY = Math.abs(touch.clientY - startY);

      if (distanceX > 12 || distanceY > 12) {
        didMove = true;
        clearTimeout(pressTimer);
      }
    }, { passive: true });

    taskItem.addEventListener("touchend", () => {
      clearTimeout(pressTimer);
    });

    taskItem.addEventListener("touchcancel", () => {
      clearTimeout(pressTimer);
    });
  }
}

function autoScrollWhileDragging(e) {
  const margin = 80;
  const speed = 18;

  const scrollContainer = document.getElementById("weekBoardScroll");

  if (!scrollContainer) return;

  const rect = scrollContainer.getBoundingClientRect();

  if (e.clientY < rect.top + margin) {
    scrollContainer.scrollTop -= speed;
  }

  if (e.clientY > rect.bottom - margin) {
    scrollContainer.scrollTop += speed;
  }

  if (e.clientX < rect.left + margin) {
    scrollContainer.scrollLeft -= speed;
  }

  if (e.clientX > rect.right - margin) {
    scrollContainer.scrollLeft += speed;
  }
}

// FIN NUEVO

function addTaskInteractionHandlers(taskItem, taskId) {
  const openMenu = (x, y) => {
    openTaskMenu(taskId, x, y);
  };

  // Desktop: solo click derecho abre menú
  taskItem.addEventListener("contextmenu", (e) => {
    e.preventDefault();
    e.stopPropagation();
    openMenu(e.clientX, e.clientY);
  });

  // Táctil: mantener apretado abre menú
  if (isTouchDevice()) {
    let pressTimer = null;
    let startX = 0;
    let startY = 0;
    let didMove = false;

    taskItem.addEventListener("touchstart", (e) => {
      const touch = e.touches[0];

      startX = touch.clientX;
      startY = touch.clientY;
      didMove = false;

      pressTimer = setTimeout(() => {
        if (!didMove) {
          openMenu(touch.clientX, touch.clientY);
        }
      }, 700);
    });

    taskItem.addEventListener("touchmove", (e) => {
      const touch = e.touches[0];

      const distanceX = Math.abs(touch.clientX - startX);
      const distanceY = Math.abs(touch.clientY - startY);

      if (distanceX > 10 || distanceY > 10) {
        didMove = true;
        clearTimeout(pressTimer);
      }
    });

    taskItem.addEventListener("touchend", () => {
      clearTimeout(pressTimer);
    });

    taskItem.addEventListener("touchcancel", () => {
      clearTimeout(pressTimer);
    });
  }
}
// FIN NUEVO

function formatDate(year, month, day) {
  const mm = String(month + 1).padStart(2, "0");
  const dd = String(day).padStart(2, "0");
  return `${year}-${mm}-${dd}`;
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

//NUEVO
function isToday(dateString) {
  const today = new Date();

  const todayString = formatDate(
    today.getFullYear(),
    today.getMonth(),
    today.getDate()
  );

  return dateString === todayString;
}
//FIN NUEVO