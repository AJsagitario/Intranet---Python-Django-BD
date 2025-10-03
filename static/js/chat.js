(function(){
  const form  = document.getElementById('chatForm');
  if(!form) return;

  const input = document.getElementById('chatInput');
  const list  = document.getElementById('messages');
  const send  = document.getElementById('sendBtn');
  const emoji = document.getElementById('emojiBtn');
  const room  = form.dataset.room;
  const me    = form.dataset.me;

  const proto = (location.protocol === "https:") ? "wss" : "ws";
  const ws = new WebSocket(`${proto}://${location.host}/ws/chat/${room}/`);

  ws.onmessage = (e)=>{
    const data = JSON.parse(e.data);
    const div = document.createElement('div');
    div.className = 'msg ' + (data.user === me ? 'me' : 'other');
    div.innerHTML = `<strong>${data.user}</strong>: ${data.body} <small>${new Date(data.ts).toLocaleTimeString()}</small>`;
    list.appendChild(div);
    list.scrollTop = list.scrollHeight;
  };

  // habilita/deshabilita botón
  const toggleBtn = ()=> send.disabled = !input.value.trim().length;
  input.addEventListener('input', toggleBtn);
  toggleBtn();

  // Enter para enviar, Shift+Enter = salto de línea
  input.addEventListener('keydown', (ev)=>{
    if(ev.key === 'Enter' && !ev.shiftKey){
      ev.preventDefault();
      send.click();
    }
  });

  // auto-grow del textarea
  const autoGrow = ()=>{
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 160) + 'px';
  };
  input.addEventListener('input', autoGrow);
  autoGrow();

  // botón emoji (inserta nativo)
  emoji.addEventListener('click', ()=>{
    input.setRangeText('😊', input.selectionStart, input.selectionEnd, 'end');
    input.dispatchEvent(new Event('input'));
    input.focus();
  });

  form.addEventListener('submit', (ev)=>{
    ev.preventDefault();
    const body = input.value.trim();
    if(!body) return;
    ws.send(JSON.stringify({ body }));
    input.value = '';
    input.dispatchEvent(new Event('input')); // para actualizar altura y botón
  });
})();
