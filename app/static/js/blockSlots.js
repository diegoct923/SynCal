function formatHour(hour) {
  const h = Math.floor(hour);
  const m = Math.round((hour - h) * 60);
  const result = `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
  return result;
}

function getUniqueBlocksForDisplay(list) {
  const grouped = {};

  list.forEach(slot => {
    if (!grouped[slot.id]) {
      grouped[slot.id] = { ...slot, days: [] };
    }
    if (slot.repeatEveryDay) {
      grouped[slot.id].repeatEveryDay = true;
    } else {
      grouped[slot.id].days.push(slot.day);
    }
  });

  return Object.values(grouped).map(slot => {
    if (!slot.repeatEveryDay && slot.days.length === 7) {
      slot.repeatEveryDay = true;
    }
    return slot;
  });
}

function openBlockedSlotsModal() {
  const dayOptions = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];

  const uniqueActive = getUniqueBlocksForDisplay(blockedTimeSlots);
  const uniqueHidden = getUniqueBlocksForDisplay(hiddenBlockedSlots);

  const isOwnBlock = (slot) => blockedTimeSlots.find(b => b.id === slot.id)?.usuario_tel != null
    || !uniqueHidden.find(h => h.id === slot.id) && slot.day !== null && !slot.repeatEveryDay && false; // marcador, ver nota abajo

  const currentBlocksHTML = uniqueActive.map(slot => {
    const label = slot.repeatEveryDay ? "Todos los días" : slot.days.map(d => dayOptions[d]).join(", ");
    return `
      <div class="blocked-slot-row">
        <strong>${label}</strong>
        <span>${slot.title} - ${formatHour(slot.startHour)} a ${formatHour(slot.startHour + slot.duration)}</span>
        <button type="button" onclick="toggleBlockedSlot(${slot.id})">Eliminar</button>
      </div>
    `;
  }).join("");

  const hiddenBlocksHTML = uniqueHidden.map(slot => {
    const label = slot.repeatEveryDay ? "Todos los días" : slot.days.map(d => dayOptions[d]).join(", ");
    return `
      <div class="blocked-slot-row blocked-slot-row-hidden">
        <strong>${label}</strong>
        <span>${slot.title} - ${formatHour(slot.startHour)} a ${formatHour(slot.startHour + slot.duration)}</span>
        <button type="button" onclick="toggleBlockedSlot(${slot.id})">Reactivar</button>
      </div>
    `;
  }).join("");

  openCustomModal(
    "Editar franjas bloqueadas",
    `
      <label for="blockedTitleInput">Nombre</label>
      <input id="blockedTitleInput" type="text" placeholder="Ej: Clase, trabajo, sueño">

      <label for="blockedDaySelect">Día</label>
      <select id="blockedDaySelect">
        <option value="0">Lunes</option>
        <option value="1">Martes</option>
        <option value="2">Miércoles</option>
        <option value="3">Jueves</option>
        <option value="4">Viernes</option>
        <option value="5">Sábado</option>
        <option value="6">Domingo</option>
      </select>

      <label for="blockedHourInput">Hora de inicio</label>
      <input id="blockedHourInput" type="number" min="0" max="23" value="8">

      <label for="blockedDurationInput">Duración</label>
      <input id="blockedDurationInput" type="number" min="1" max="24" value="1">

      <div class="custom-modal-message" id="blockedSlotError"></div>

      <hr>

      <h3>Bloqueos actuales</h3>
      <div class="blocked-slot-list">
        ${currentBlocksHTML || "<p>No hay franjas bloqueadas.</p>"}
      </div>

      ${uniqueHidden.length > 0 ? `
        <hr>
        <h3>Bloqueos ocultos</h3>
        <div class="blocked-slot-list blocked-slot-list-hidden">
          ${hiddenBlocksHTML}
        </div>
      ` : ""}
    `,
    () => {
      const title = document.getElementById("blockedTitleInput").value.trim();
      const day = Number(document.getElementById("blockedDaySelect").value);
      const hour = Number(document.getElementById("blockedHourInput").value);
      const duration = Number(document.getElementById("blockedDurationInput").value);
      const error = document.getElementById("blockedSlotError");

      if (Number.isNaN(hour) || hour < 0 || hour > 23) {
        error.textContent = "La hora debe estar entre 0 y 23.";
        return;
      }

      if (Number.isNaN(duration) || duration < 1 || duration > 24) {
        error.textContent = "La duración debe estar entre 1 y 24 horas.";
        return;
      }

      if (hour + duration > 24) {
        error.textContent = "El bloqueo no puede terminar después de las 24:00.";
        return;
      }

      createBlockedSlot(day, hour, duration, title);
      closeCustomModal();
    },
    "Agregar bloqueo"
  );
}

manageBlocksBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  calendarOptionsPanel.classList.add("hidden");
  openBlockedSlotsModal();
});