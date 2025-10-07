document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("taskSearch");
  const allTasks = document.querySelectorAll(".task-item");

  if (!searchInput) return;

  searchInput.addEventListener("input", () => {
    const q = searchInput.value.trim().toLowerCase();
    allTasks.forEach((item) => {
      const text = item.textContent.toLowerCase();
      item.style.display = text.includes(q) ? "" : "none";
    });
  });
});
