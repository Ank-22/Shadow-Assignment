## Python backend (step 1)

Minimal CLI that loads input images, a foreground mask, and writes a projected shadow.

### Usage

```bash
python backend/main.py \
  --fg "Shadow-Files-main/25_1107O_11974 PB + 1 - Photo Calendar B_Lamborghini HAS.JPG" \
  --bg "Shadow-Files-main/B_Lamborghini Red.JPG" \
  --out-dir outputs \
  --angle 45 \
  --elevation 45
```

`--mask` is optional. If omitted, the CLI uses the foreground alpha channel.

Outputs:
- `outputs/composite.png`
- `outputs/shadow_only.png`
- `outputs/mask_debug.png`

### UI server

```bash
python backend/server.py
```

Open `http://localhost:8000` to use the HTML UI.
