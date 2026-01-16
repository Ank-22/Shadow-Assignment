Hi! 👋

Thank you for choosing to join our team. We’d like to give you a small mini-challenge to confirm skills in **Python / TypeScript** (your choice). ✅

---

## 🎯 Mini Challenge: Realistic Shadow Generator

Build a mini app that takes:

- 🧍‍♂️ **Foreground image** (you should cut out the subject)
- 🏫 **Background image**
- ⭐ **Bonus:** 🌫️ **Depth map** (grayscale 0–255)

…and outputs a final composite where the foreground casts a **realistic-looking shadow** on the background (not just a blur + offset).

---

## ✅ Requirements (must have)

### 💡 Directional light control
- Light angle (0–360°)
- Light elevation (0–90°)

### 🖤 Contact shadow
- Dark and sharp near the feet / contact area
- Quickly fades out with distance

### 🌫️ Soft shadow falloff
- Blur increases as the shadow moves farther away
- Opacity decreases with distance

### ✂️ Shadow must match the subject silhouette
- No oval shadow
- No fake drop-shadow filter

---

## ⭐ Bonus Mode (advanced)

If a **depth map** is provided:

- Shadow should bend / warp using the depth map  
  (more realistic shadow behavior on uneven surfaces)

---

## 🧰 Deliverables

Please submit:

- `composite.png` 🖼️ (final output)
- `shadow_only.png` 🖤 (debug)
- `mask_debug.png` ✂️ (debug)
- **Source code + README** 📄

You can build it as:

- 🌐 **Web app (TypeScript)** OR
- 🐍 **Python CLI / PyQt6 UI**

> Bonus points if you can show you know how to use both.

---

## 📝 What we’re looking for

We don’t need perfect physics — we want something that:
- Looks believable
- Works on different images
- Shows real compositing + shadow math 💪

---

### ⏰ Deadline
**2–3 days**

### 🔗 Resources
GitHub repo with foreground and background images:  
https://github.com/amcnyusa/Shadow-Files

---

## Project setup (local)

### Python backend (CLI)

```bash
pip install -r backend/requirements.txt
python backend/main.py \
  --fg "Shadow-Files-main/25_1107O_11974 PB + 1 - Photo Calendar B_Lamborghini HAS.JPG" \
  --bg "Shadow-Files-main/B_Lamborghini Red.JPG" \
  --mask "path/to/mask.png" \
  --out-dir outputs \
  --angle 45 \
  --elevation 45 \
  --soft-fade 1.0 \
  --blur-ratio 6.0
```

Notes:
- `--mask` is optional; if omitted, the foreground alpha channel is used.
- Outputs: `outputs/composite.png`, `outputs/shadow_only.png`, `outputs/mask_debug.png`.

### UI (HTML + TypeScript)

```bash
pip install -r backend/requirements.txt
python backend/server.py
```

Open `http://localhost:8000`.

UI controls:
- Angle and elevation sliders.
- Gradient length (soft-fade) slider.
- Blur ratio slider.
- Save buttons add angle/elevation to filenames.
