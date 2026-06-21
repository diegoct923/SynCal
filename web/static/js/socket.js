const socket = io({
    query: { state: APP_STATE }
});

socket.on("connect", () => {
    console.log("[socket] conectado");
});

socket.on("task_created", (task) => {
    loadTasksFromBackend();
});

socket.on("task_updated", (data) => {
    const task = tasks.find(t => t.id === data.id);
    if (!task) return;

    if (data.status === "COMPLETADA") task.priority = "completada";
    if (data.title) task.title = data.title;
    if (data.priority) task.priority = data.priority;
    if (data.deadline) {
        const deadlineValue = data.deadline.replace(" ", "T");
        const deadline = new Date(deadlineValue);

        task.date = deadlineValue.split("T")[0];
        task.startHour = deadline.getHours() + deadline.getMinutes() / 60;
    }

    renderCalendar();
});

socket.on("task_deleted", (data) => {
    loadTasksFromBackend();
});

socket.on("disconnect", () => {
    console.log("[socket] desconectado");
});

socket.on("blocked_slot_created", (slot) => {
    loadTasksFromBackend();
});

socket.on("blocked_slot_toggled", (data) => {
    loadTasksFromBackend();
});

socket.on("blocked_slot_deleted", (data) => {
    loadTasksFromBackend();
});
