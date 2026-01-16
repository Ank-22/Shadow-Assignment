const fgInput = document.getElementById("fg") as HTMLInputElement;
const bgInput = document.getElementById("bg") as HTMLInputElement;
const maskInput = document.getElementById("mask") as HTMLInputElement;
const angleInput = document.getElementById("angle") as HTMLInputElement;
const elevationInput = document.getElementById("elevation") as HTMLInputElement;
const angleValue = document.getElementById("angle-value") as HTMLSpanElement;
const elevationValue = document.getElementById("elevation-value") as HTMLSpanElement;
const status = document.getElementById("status") as HTMLParagraphElement;
const composeButton = document.getElementById("compose") as HTMLButtonElement;

const fgPreview = document.getElementById("fg-preview") as HTMLImageElement;
const bgPreview = document.getElementById("bg-preview") as HTMLImageElement;
const maskPreview = document.getElementById("mask-preview") as HTMLImageElement;
const compositePreview = document.getElementById("composite-preview") as HTMLImageElement;
const shadowPreview = document.getElementById("shadow-preview") as HTMLImageElement;

const updateSliderLabels = () => {
  angleValue.textContent = `${angleInput.value}°`;
  elevationValue.textContent = `${elevationInput.value}°`;
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

  const form = new FormData();
  form.append("fg", fgInput.files![0]);
  form.append("bg", bgInput.files![0]);
  if (maskInput.files && maskInput.files[0]) {
    form.append("mask", maskInput.files[0]);
  }
  form.append("angle", angleInput.value);
  form.append("elevation", elevationInput.value);

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

    compositePreview.src = `data:image/png;base64,${data.composite}`;
    shadowPreview.src = `data:image/png;base64,${data.shadow_only}`;
    setStatus("Done. Adjust the sliders and run again.");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    setStatus(message, true);
  } finally {
    composeButton.disabled = false;
  }
};

updateSliderLabels();

fgInput.addEventListener("change", () => updatePreview(fgInput, fgPreview));
bgInput.addEventListener("change", () => updatePreview(bgInput, bgPreview));
maskInput.addEventListener("change", () => updatePreview(maskInput, maskPreview));
angleInput.addEventListener("input", updateSliderLabels);
elevationInput.addEventListener("input", updateSliderLabels);
composeButton.addEventListener("click", compose);
