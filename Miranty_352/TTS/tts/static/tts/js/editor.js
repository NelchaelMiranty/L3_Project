document.addEventListener("DOMContentLoaded", () => {
  const cfg = window.VOX_SYNTH || {};
  const form = document.getElementById("tts-form");
  const textInput = document.getElementById("text");
  const seedInput = document.getElementById("seed");
  const ritmaInput = document.getElementById("ritma");
  const fiovanRitmaInput = document.getElementById("fiovan-ritma");
  const angolaInput = document.getElementById("angola");
  const ritmaVal = document.getElementById("ritma-val");
  const fiovanRitmaVal = document.getElementById("fiovan-ritma-val");
  const angolaVal = document.getElementById("angola-val");
  const generateBtn = document.getElementById("generate-btn");
  const statusEl = document.getElementById("status");
  const charCount = document.getElementById("char-count");
  const player = document.getElementById("player");
  const playBtn = document.getElementById("play-btn");
  const playIcon = document.getElementById("play-icon");
  const timeDisplay = document.getElementById("time-display");
  const downloadLink = document.getElementById("download");
  const waveformContainer = document.getElementById("waveform-container");

  let audioUrl = null;
  let audioContext = null;

  function setStatus(message, isError = false) {
    if (!statusEl) return;
    statusEl.textContent = message;
    statusEl.classList.toggle("error", isError);
  }

  function revokeAudioUrl() {
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      audioUrl = null;
    }
  }

  function updateCharCount() {
    if (charCount && textInput) {
      charCount.textContent = `${textInput.value.length} caractères`;
    }
  }

  if (textInput) {
    textInput.addEventListener("input", updateCharCount);
    updateCharCount();
  }

  function bindSlider(input, label, decimals = 2) {
    if (!input || !label) return;
    const update = () => {
      label.textContent = Number(input.value).toFixed(decimals);
    };
    input.addEventListener("input", update);
    update();
  }

  bindSlider(ritmaInput, ritmaVal);
  bindSlider(fiovanRitmaInput, fiovanRitmaVal);
  bindSlider(angolaInput, angolaVal);

  document.querySelectorAll(".example-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      textInput.value = chip.dataset.example;
      updateCharCount();
      textInput.focus();
    });
  });

  function setDownloadEnabled(enabled) {
    if (!downloadLink) return;
    downloadLink.classList.toggle("pointer-events-none", !enabled);
    downloadLink.classList.toggle("opacity-40", !enabled);
    if (!enabled) downloadLink.href = "#";
  }

  function setupPlayback() {
    if (!player) return;

    player.addEventListener("timeupdate", () => {
      const cur = player.currentTime || 0;
      const dur = player.duration || 0;
      if (timeDisplay) {
        timeDisplay.textContent = `${window.VoxSynthUI.formatTime(cur)} / ${window.VoxSynthUI.formatTime(dur)}`;
      }
      if (dur > 0) {
        window.VoxSynthUI.updateWaveformProgress(waveformContainer, cur / dur);
      }
    });

    player.addEventListener("ended", () => {
      if (playIcon) playIcon.textContent = "play_arrow";
    });

    playBtn?.addEventListener("click", () => {
      if (!player.src) return;
      if (player.paused) {
        player.play().catch(() => {});
        playIcon.textContent = "pause";
      } else {
        player.pause();
        playIcon.textContent = "play_arrow";
      }
    });
  }

  setupPlayback();

  async function decodeWaveform(blob) {
    try {
      audioContext = audioContext || new AudioContext();
      const buffer = await blob.arrayBuffer();
      const audioBuffer = await audioContext.decodeAudioData(buffer.slice(0));
      const data = audioBuffer.getChannelData(0);
      window.VoxSynthUI.drawWaveformFromBuffer(waveformContainer, data);
    } catch {
      window.VoxSynthUI.initIdleWaveform(waveformContainer);
    }
  }

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = textInput.value.trim();
    if (!text) {
      setStatus("Entrez du texte en malgache.", true);
      return;
    }

    const csrfToken =
      form.querySelector("[name=csrfmiddlewaretoken]")?.value || cfg.csrfToken;

    generateBtn.disabled = true;
    if (playBtn) playBtn.disabled = true;
    setDownloadEnabled(false);
    setStatus("Synthèse en cours…");

    try {
      const response = await fetch(cfg.synthesizeUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          text,
          seed: Number(seedInput?.value) || cfg.defaultSeed,
          ritma: Number(ritmaInput?.value) ?? 0.75,
          fiovan_ritma: Number(fiovanRitmaInput?.value) ?? 0.4,
          angola: Number(angolaInput?.value) ?? 0.4,
        }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || "Erreur lors de la synthèse.");
      }

      revokeAudioUrl();
      const blob = await response.blob();
      audioUrl = URL.createObjectURL(blob);

      player.src = audioUrl;
      downloadLink.href = audioUrl;
      setDownloadEnabled(true);
      if (playBtn) playBtn.disabled = false;

      await decodeWaveform(blob);
      await player.play().catch(() => {});
      if (playIcon) playIcon.textContent = "pause";

      const duration = response.headers.get("X-Audio-Duration");
      setStatus(duration ? `Audio généré (${duration} s).` : "Audio généré.");
    } catch (error) {
      setStatus(error.message, true);
    } finally {
      generateBtn.disabled = false;
    }
  });
});
