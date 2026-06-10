const BASE_URL = "https://unastonished-arlie-interligamentous.ngrok-free.dev";


// obtener tareas

async function apiGetTasks(state) {

  const response = await fetch(
    `${BASE_URL}/api/tasks?state=${state}`
  );

  if (!response.ok) {
    throw new Error("No se pudieron obtener las tareas");
  }

  return await response.json();
}



// crear tarea

async function apiCreateTask(taskData, state) {

  const response = await fetch(
    `${BASE_URL}/api/tasks/create`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        ...taskData,
        state
      })
    }
  );

  if (!response.ok) {
    throw new Error("No se pudo crear la tarea");
  }

  return await response.json();
}



// reagendar

async function apiUpdateTask(taskData, state) {

  const response = await fetch(
    `${BASE_URL}/api/tasks/reagendar`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        ...taskData,
        state
      })
    }
  );

  if (!response.ok) {
    throw new Error("No se pudo reagendar la tarea");
  }

  return await response.json();
}



// completar

async function apiCompleteTask(task_id, state) {

  const response = await fetch(
    `${BASE_URL}/api/tasks/complete`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        task_id,
        state
      })
    }
  );

  if (!response.ok) {
    throw new Error("No se pudo completar la tarea");
  }

  return await response.json();
}



// borrar

async function apiDeleteTask(task_id, state) {

  const response = await fetch(
    `${BASE_URL}/api/tasks/delete`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        task_id,
        state
      })
    }
  );

  if (!response.ok) {
    throw new Error("No se pudo borrar la tarea");
  }

  return await response.json();
}

async function apiGetBlockedSlots(state) {
  const response = await fetch(
    `${BASE_URL}/api/tasks/blocked-slots?state=${state}`
  );

  if (!response.ok) {
    throw new Error("No se pudieron obtener las franjas bloqueadas");
  }

  return await response.json();
}