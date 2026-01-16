## Python backend (step 1)

Minimal CLI that loads input images, a foreground mask, and writes a projected shadow.

### Usage

```bash
python backend/main.py \
  --fg "Shadow-Files-main/25_1107O_11974 PB + 1 - Photo Calendar B_Lamborghini HAS.JPG" \
  --bg "Shadow-Files-main/B_Lamborghini Red.JPG" \
  --mask "path/to/mask.png" \
  --out-dir outputs
```

Outputs:
- `outputs/composite.png`
- `outputs/shadow_only.png`
- `outputs/mask_debug.png`
