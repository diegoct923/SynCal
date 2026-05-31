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
        task.date = data.deadline.split("T")[0];
        task.startHour = new Date(data.deadline.replace(" ", "T")).getHours();
    }

    renderCalendar();
});

socket.on("task_deleted", (data) => {
    loadTasksFromBackend();
});

socket.on("disconnect", () => {
    console.log("[socket] desconectado");
});