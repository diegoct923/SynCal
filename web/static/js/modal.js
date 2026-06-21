let modalAction = null;

function openCustomModal(title, bodyHTML, onSave, saveText = "Guardar", danger = false) {
  customModalTitle.textContent = title;
  customModalBody.innerHTML = bodyHTML;
  modalAction = onSave;

  customModalSave.textContent = saveText;
  customModalSave.classList.remove("danger");

  if (danger) {
    customModalSave.classList.add("danger");
  }

  customModalOverlay.classList.remove("hidden");
}

function closeCustomModal() {
  customModalOverlay.classList.add("hidden");
  customModalBody.innerHTML = "";
  modalAction = null;
}

customModalSave.addEventListener("click", () => {
  if (typeof modalAction === "function") {
    modalAction();
  }
});


function openConfirmBlockedSlotModal(onConfirm, onCancel, conflict) {
  openCustomModal(
    "Franja bloqueada",
    `
      <p>Estás intentando crear una tarea dentro de una franja bloqueada.</p>

      <p>
        <strong>${conflict.title}</strong><br>
        ${formatHour(conflict.startHour)} - ${formatHour(conflict.startHour + conflict.duration)}
      </p>

      <p>¿Querés crear la tarea ahí de todas formas?</p>
    `,
    () => {
      onConfirm();
      closeCustomModal();
    },
    "Crear igual",
    true
  );

  customModalCancel.onclick = (e) => {
    e.preventDefault();
    e.stopPropagation();

    onCancel();
    closeCustomModal();
  };
}

customModalCancel.addEventListener("click", closeCustomModal);
customModalClose.addEventListener("click", closeCustomModal);

customModalOverlay.addEventListener("click", (e) => {
  if (e.target === customModalOverlay) {
    closeCustomModal();
  }
});