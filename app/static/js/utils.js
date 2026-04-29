const monthNames = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
];

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