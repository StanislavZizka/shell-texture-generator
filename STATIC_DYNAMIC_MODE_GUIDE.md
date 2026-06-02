# Static/Dynamic Mode - User Guide

## Overview

Shell Texture Generator now has **two modes** for generating patterns:

- **🔒 Static Mode** - Simplified, preset-based generation
- **🔓 Dynamic Mode** - Advanced, full parameter control

---

## 🔒 Static Mode

**Best for:** Quick experiments, reproducible results, beginners

### How it works:

1. Select a **preset** from the dropdown
2. All Gierer-Meinhardt parameters are **automatically set** (visible but locked)
3. You can still adjust: K, t_max, delta_t, colors
4. Click **Generate Texture**

### Available Presets:

| Preset | D_b Value | Result |
|--------|-----------|--------|
| **Low Diffusion** | 0.25 | Sharp, well-defined patterns (spots, stripes) |
| **Medium Diffusion** | 0.35 | Balanced wave-like patterns |
| **High Diffusion** | 0.50 | Soft, smooth gradients |

### Parameters in Static Mode:

```
✅ Editable:
   - K (Reaction constant)
   - t_max (Simulation time)
   - delta_t (Time step)
   - Color1, Color2

🔒 Locked (from preset):
   - s (Autocatalysis strength)
   - D_b (Inhibitor diffusion)
   - r_a (Activator decay)
   - r_b (Inhibitor decay)
   - B0 (Initial inhibitor)
```

### Example Use Case:

> "I want to generate a shell pattern similar to *Conus marmoreus* (sharp stripes)"
>
> → Select **Low Diffusion** preset
> → Adjust K and t_max if needed
> → Generate

---

## 🔓 Dynamic Mode

**Best for:** Experimentation, custom patterns, advanced users

### How it works:

1. Switch to **Dynamic Mode** (toggle at top)
2. **All parameters are editable** (no presets)
3. Manually set: s, D_b, r_a, r_b, K, t_max, delta_t
4. Click **Generate Texture**

### When to use:

- 🧪 Experimenting with specific parameter combinations
- 📊 Testing mathematical hypotheses
- 🎨 Creating unique, non-standard patterns
- 📚 Following scientific literature (specific parameter values)

### Full Control:

All Gierer-Meinhardt equation parameters are editable:

```
s     - Autocatalysis strength (0.01 - 0.20)
D_b   - Inhibitor diffusion (0.10 - 0.80)
r_a   - Activator decay rate (0.01 - 0.30)
r_b   - Inhibitor decay rate (0.01 - 0.30)
K     - Reaction constant (0.0001 - 5.0)
t_max - Maximum simulation time (1.0 - 10000.0)
delta_t - Time step (0.001 - 1.0)
```

### Example Use Case:

> "I'm following Meinhardt's paper (1995) and want to test parameters: s=0.13, D_b=0.28, r_a=0.05"
>
> → Switch to **Dynamic Mode**
> → Enter custom values
> → Generate

---

## 🧬 Random Error (Both Modes)

**Random Error (Biological Perturbation)** is available in **both modes**:

- ☑ Enable Random Error checkbox
- Adjust strength, duration, frequency
- Simulates natural defects in shell growth

**Works identically in both Static and Dynamic modes.**

---

## 📊 Analysis Tools (Both Modes)

These features work in **both modes**:

### ☑ Show Pattern Evolution (4 stages)
- Exports snapshots at 25%, 50%, 75%, 100% of simulation
- Shows how patterns develop over time
- Useful for understanding dynamics

### ☑ Show Analysis Grid
- 2x2 comparison grid
- Multiple parameter variations side-by-side

### ☑ Show Biological Heatmap
- Color overlay showing activator concentration
- Blue = low activity, Red = high activity
- Helps identify pattern hotspots

---

## Quick Start Examples

### Example 1: Simple Stripe Pattern (Static Mode)

```
Mode: Static Mode
Preset: Low Diffusion
K: 1.0
t_max: 400
delta_t: 0.025
Colors: Blue + Red
Random Error: OFF
```

**Result:** Clean, sharp stripes

---

### Example 2: Soft Gradient (Static Mode)

```
Mode: Static Mode
Preset: High Diffusion
K: 0.5
t_max: 600
delta_t: 0.025
Colors: Blue + Yellow
Random Error: OFF
```

**Result:** Smooth, cloud-like gradients

---

### Example 3: Custom Experiment (Dynamic Mode)

```
Mode: Dynamic Mode
s: 0.13
D_b: 0.30
r_a: 0.06
r_b: 0.12
K: 1.2
t_max: 500
delta_t: 0.025
Colors: Green + Orange
Random Error: ON (moderate)
```

**Result:** Unique pattern with biological defects

---

## Switching Between Modes

### Static → Dynamic:

1. Click **Dynamic Mode** button
2. Parameters unlock for editing
3. Previous preset values remain visible
4. Edit as needed

### Dynamic → Static:

1. Click **Static Mode** button
2. Select a preset
3. Parameters lock automatically
4. Custom values are discarded (preset values applied)

**Note:** Switching modes does NOT trigger regeneration - you must click **Generate Texture**.

---

## Tips & Best Practices

### For Static Mode:

✅ Start with **Medium Diffusion** for balanced results
✅ Try different presets before adjusting K
✅ Use **Pattern Evolution** to see how each preset develops

### For Dynamic Mode:

✅ Start with preset values and modify gradually
✅ Keep `D_b > D_a` (inhibitor diffuses faster than activator)
✅ If simulation explodes, reduce `s` or increase `r_a`
✅ Use smaller `delta_t` for numerical stability

### General:

✅ Enable **Biological Heatmap** to understand pattern formation
✅ Use **Random Error** sparingly (start with low strength)
✅ Save successful parameter combinations (screenshot or notes)

---

## Troubleshooting

### Pattern looks uniform (no structure):

- **Static Mode:** Try **Low Diffusion** preset
- **Dynamic Mode:** Increase `s` or decrease `D_b`
- Increase `t_max` (pattern needs more time to form)

### Simulation explodes (all white or all black):

- **Static Mode:** Reduce `K` or change preset
- **Dynamic Mode:** Decrease `s`, increase `r_a`, or use smaller `delta_t`

### Pattern too noisy/chaotic:

- **Static Mode:** Try **High Diffusion** preset
- **Dynamic Mode:** Increase `D_b` or decrease `s`
- Disable Random Error if enabled

---

## What Happened to Old Features?

### Removed from UI:

❌ **Old Presets** (Stable/Balanced/Active/Chaotic)
   - Replaced by Low/Medium/High Diffusion
   - More intuitive, clearer results

❌ **Dynamic Instability**
   - Redundant with Random Error
   - Random Error is better (localized, scientifically grounded)

❌ **Compare with Baseline**
   - Limited usefulness (visual only, no metrics)
   - May return in future with quantitative analysis

### Still Available:

✅ **Random Error** - fully functional
✅ **Pattern Evolution** - 4-stage snapshots
✅ **Analysis Grid** - side-by-side comparisons
✅ **Biological Heatmap** - concentration visualization

**All removed features are archived** (see `archived/ARCHIVED_FEATURES.md`).

---

## FAQ

**Q: Can I still get the old "Stable" preset behavior?**
A: Use **High Diffusion** (similar soft patterns) or **Medium Diffusion** (balanced).

**Q: What if I want full control like the old system?**
A: Use **Dynamic Mode** - you have more control than before!

**Q: Why were old presets removed?**
A: The new system is simpler and more predictable. Old presets had overlapping behaviors.

**Q: Can I restore the old UI?**
A: Yes, see `MIGRATION_GUIDE.md` rollback section.

**Q: Do I need to change my saved parameter combinations?**
A: No, just enter them manually in Dynamic Mode.

---

## Learn More

- **Scientific Background:** See `README.md` for Gierer-Meinhardt equations
- **Random Error Details:** See `services/random_error_module.py` documentation
- **Migration Guide:** See `MIGRATION_GUIDE.md` for technical details
- **Archived Features:** See `archived/ARCHIVED_FEATURES.md`

---

**Enjoy exploring shell patterns! 🐚**
