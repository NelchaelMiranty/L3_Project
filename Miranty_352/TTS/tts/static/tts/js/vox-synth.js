function toggleSidebar(forceClose) {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar) return;
  if (forceClose) {
    sidebar.classList.add("-translate-x-full");
    return;
  }
  sidebar.classList.toggle("-translate-x-full");
}

function initSidebar() {
  const menuBtn = document.getElementById("menu-btn");
  if (menuBtn) {
    menuBtn.addEventListener("click", () => toggleSidebar());
  }
  document.addEventListener("click", (e) => {
    const sidebar = document.getElementById("sidebar");
    const menuBtn = document.getElementById("menu-btn");
    if (
      window.innerWidth < 768 &&
      sidebar &&
      menuBtn &&
      !sidebar.contains(e.target) &&
      !menuBtn.contains(e.target)
    ) {
      sidebar.classList.add("-translate-x-full");
    }
  });
}

function formatTime(seconds) {
  const s = Math.max(0, Math.floor(seconds));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${String(m).padStart(2, "0")}:${String(r).padStart(2, "0")}`;
}

function initIdleWaveform(container, barCount) {
  if (!container || container.dataset.initialized) return;
  const count = barCount || (container.classList.contains("flex-col") ? 40 : 80);
  container.dataset.initialized = "1";
  container.innerHTML = "";
  for (let i = 0; i < count; i++) {
    const bar = document.createElement("div");
    bar.className = "waveform-bar w-1 rounded-full bg-gradient-to-t from-secondary to-tertiary opacity-30";
    bar.style.height = `${Math.floor(Math.random() * 60) + 15}%`;
    container.appendChild(bar);
  }
}

function drawWaveformFromBuffer(container, channelData, barCount) {
  if (!container) return;
  const count = barCount || Math.min(80, Math.max(40, Math.floor(container.clientWidth / 4)));
  container.innerHTML = "";
  const step = Math.floor(channelData.length / count) || 1;
  for (let i = 0; i < count; i++) {
    let sum = 0;
    const start = i * step;
    for (let j = 0; j < step && start + j < channelData.length; j++) {
      sum += Math.abs(channelData[start + j]);
    }
    const h = Math.min(100, Math.max(8, (sum / step) * 400));
    const bar = document.createElement("div");
    bar.className = "waveform-bar w-1 rounded-full bg-gradient-to-t from-secondary to-tertiary opacity-30";
    bar.style.height = `${h}%`;
    bar.dataset.index = String(i);
    container.appendChild(bar);
  }
}

function updateWaveformProgress(container, progress) {
  if (!container) return;
  const bars = container.querySelectorAll(".waveform-bar");
  const playedCount = Math.floor(bars.length * progress);
  bars.forEach((bar, i) => {
    if (i < playedCount) {
      bar.classList.remove("opacity-30");
      bar.classList.add("opacity-100");
      bar.style.boxShadow = "0 0 10px rgba(137, 206, 255, 0.4)";
    } else {
      bar.classList.add("opacity-30");
      bar.classList.remove("opacity-100");
      bar.style.boxShadow = "";
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initSidebar();
  const waveformContainer = document.getElementById("waveform-container");
  if (waveformContainer) initIdleWaveform(waveformContainer);
});

window.VoxSynthUI = {
  toggleSidebar,
  formatTime,
  initIdleWaveform,
  drawWaveformFromBuffer,
  updateWaveformProgress,
};
