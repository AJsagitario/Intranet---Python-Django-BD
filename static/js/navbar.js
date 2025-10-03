// Marca enlace activo según la ruta actual
(function(){
  const path = location.pathname;
  document.querySelectorAll('.mainnav a').forEach(a=>{
    const key = a.getAttribute('data-active');
    if (!key) return;
    // Ajusta coincidencias cuando tengas rutas reales
    if (key === 'chat' && (path==='/' || path.startsWith('/c/'))) a.classList.add('active');
    if (key === 'files' && path.startsWith('/files')) a.classList.add('active');
    if (key === 'tasks' && path.startsWith('/tasks')) a.classList.add('active');
    if (key === 'calendar' && path.startsWith('/calendar')) a.classList.add('active');
  });
})();
