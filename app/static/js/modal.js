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

customModalCancel.addEventListener("click", closeCustomModal);
customModalClose.addEventListener("click", closeCustomModal);

customModalOverlay.addEventListener("click", (e) => {
  if (e.target === customModalOverlay) {
    closeCustomModal();
  }
});