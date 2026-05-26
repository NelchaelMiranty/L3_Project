document.addEventListener("DOMContentLoaded", () => {
  const recordBtn = document.getElementById("record-btn");
  const recordLabel = document.getElementById("record-label");
  const recordTimer = document.getElementById("record-timer");
  const preview = document.getElementById("record-preview");

  if (!recordBtn || !navigator.mediaDevices) return;

  const MAX_SECONDS = 30;
  let mediaRecorder = null;
  let chunks = [];
  let timerInterval = null;
  let seconds = 0;

  function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }
    clearInterval(timerInterval);
    recordBtn.classList.remove("opacity-70");
    recordLabel.textContent = "Démarrer (30 s max)";
  }

  recordBtn.addEventListener("click", async () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      stopRecording();
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      chunks = [];
      mediaRecorder = new MediaRecorder(stream);
      seconds = 0;
      recordTimer.classList.remove("hidden");
      recordTimer.textContent = "00:00";
      recordLabel.textContent = "Arrêter";
      recordBtn.classList.add("opacity-70");

      mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
      mediaRecorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunks, { type: "audio/webm" });
        preview.src = URL.createObjectURL(blob);
        preview.classList.remove("hidden");
        recordTimer.classList.add("hidden");
      };

      mediaRecorder.start();
      timerInterval = setInterval(() => {
        seconds += 1;
        recordTimer.textContent = window.VoxSynthUI.formatTime(seconds);
        if (seconds >= MAX_SECONDS) stopRecording();
      }, 1000);
    } catch {
      recordLabel.textContent = "Micro non autorisé";
    }
  });
});
