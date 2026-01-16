const fgInput = document.getElementById("fg") as HTMLInputElement;
const bgInput = document.getElementById("bg") as HTMLInputElement;
const maskInput = document.getElementById("mask") as HTMLInputElement;
const angleInput = document.getElementById("angle") as HTMLInputElement;
const elevationInput = document.getElementById("elevation") as HTMLInputElement;
const gradientInput = document.getElementById("gradient") as HTMLInputElement;
const blurRatioInput = document.getElementById("blur-ratio") as HTMLInputElement;
const angleValue = document.getElementById("angle-value") as HTMLSpanElement;
const elevationValue = document.getElementById("elevation-value") as HTMLSpanElement;
const gradientValue = document.getElementById("gradient-value") as HTMLSpanElement;
const blurRatioValue = document.getElementById("blur-ratio-value") as HTMLSpanElement;
const status = document.getElementById("status") as HTMLParagraphElement;
const composeButton = document.getElementById("compose") as HTMLButtonElement;
const liveToggle = document.getElementById("live") as HTMLInputElement;
const downloadComposite = document.getElementById("download-composite") as HTMLButtonElement;
const downloadShadow = document.getElementById("download-shadow") as HTMLButtonElement;

const fgPreview = document.getElementById("fg-preview") as HTMLImageElement;
const bgPreview = document.getElementById("bg-preview") as HTMLImageElement;
const maskPreview = document.getElementById("mask-preview") as HTMLImageElement;
const compositePreview = document.getElementById("composite-preview") as HTMLImageElement;
const shadowPreview = document.getElementById("shadow-preview") as HTMLImageElement;

let latestComposite: string | null = null;
let latestShadow: string | null = null;
let renderTimeout: number | null = null;
let renderInFlight = false;

const updateSliderLabels = () => {
  angleValue.textContent = `${angleInput.value}°`;
  elevationValue.textContent = `${elevationInput.value}°`;
  gradientValue.textContent = `${Number(gradientInput.value).toFixed(2)}`;
  blurRatioValue.textContent = `${Number(blurRatioInput.value).toFixed(1)}`;
};

const updatePreview = (input: HTMLInputElement, img: HTMLImageElement) => {
  const file = input.files?.[0];
  if (!file) {
    img.removeAttribute("src");
    return;
  }
  const url = URL.createObjectURL(file);
  img.src = url;
  img.onload = () => URL.revokeObjectURL(url);
};

const setStatus = (message: string, isError = false) => {
  status.textContent = message;
  status.style.color = isError ? "#b01a1a" : "";
};

const setLoading = (isLoading: boolean) => {
  document.body.classList.toggle("loading", isLoading);
};

const fileRequired = (input: HTMLInputElement, label: string) => {
  if (!input.files || input.files.length === 0) {
    setStatus(`Please upload a ${label}.`, true);
    return false;
  }
  return true;
};

const compose = async () => {
  if (!fileRequired(fgInput, "foreground") || !fileRequired(bgInput, "background")) {
    return;
  }

  setStatus("Rendering shadow, please wait...");
  composeButton.disabled = true;
  renderInFlight = true;
  setLoading(true);

  const form = new FormData();
  form.append("fg", fgInput.files![0]);
  form.append("bg", bgInput.files![0]);
  if (maskInput.files && maskInput.files[0]) {
    form.append("mask", maskInput.files[0]);
  }
  form.append("angle", angleInput.value);
  form.append("elevation", elevationInput.value);
  form.append("soft_fade", gradientInput.value);
  form.append("blur_ratio", blurRatioInput.value);

  try {
    const response = await fetch("/api/compose", {
      method: "POST",
      body: form,
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || "Server error");
    }

    const data = (await response.json()) as {
      composite: string;
      shadow_only: string;
    };

    latestComposite = data.composite;
    latestShadow = data.shadow_only;
    compositePreview.src = `data:image/png;base64,${data.composite}`;
    shadowPreview.src = `data:image/png;base64,${data.shadow_only}`;
    setStatus("Done. Adjust the sliders and run again.");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    setStatus(message, true);
  } finally {
    composeButton.disabled = false;
    renderInFlight = false;
    setLoading(false);
  }
};

const scheduleRender = () => {
  if (!liveToggle.checked) {
    return;
  }
  if (renderTimeout) {
    window.clearTimeout(renderTimeout);
  }
  renderTimeout = window.setTimeout(() => {
    if (!renderInFlight) {
      compose();
    }
  }, 250);
};

const downloadFromBase64 = (data: string, filename: string) => {
  const link = document.createElement("a");
  link.href = `data:image/png;base64,${data}`;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
};

const buildFilename = (base: string) => {
  const angle = angleInput.value;
  const elevation = elevationInput.value;
  return `${base}_angle-${angle}_elev-${elevation}.png`;
};

updateSliderLabels();

fgInput.addEventListener("change", () => updatePreview(fgInput, fgPreview));
bgInput.addEventListener("change", () => updatePreview(bgInput, bgPreview));
maskInput.addEventListener("change", () => updatePreview(maskInput, maskPreview));
angleInput.addEventListener("input", updateSliderLabels);
elevationInput.addEventListener("input", updateSliderLabels);
gradientInput.addEventListener("input", updateSliderLabels);
blurRatioInput.addEventListener("input", updateSliderLabels);
composeButton.addEventListener("click", compose);
fgInput.addEventListener("change", scheduleRender);
bgInput.addEventListener("change", scheduleRender);
maskInput.addEventListener("change", scheduleRender);
angleInput.addEventListener("input", scheduleRender);
elevationInput.addEventListener("input", scheduleRender);
gradientInput.addEventListener("input", scheduleRender);
blurRatioInput.addEventListener("input", scheduleRender);

downloadComposite.addEventListener("click", () => {
  if (!latestComposite) {
    setStatus("No composite available yet.", true);
    return;
  }
  downloadFromBase64(latestComposite, buildFilename("composite"));
});

downloadShadow.addEventListener("click", () => {
  if (!latestShadow) {
    setStatus("No shadow output available yet.", true);
    return;
  }
  downloadFromBase64(latestShadow, buildFilename("shadow_only"));
});
