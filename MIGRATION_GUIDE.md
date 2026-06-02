# Migration Guide: Static/Dynamic Mode Update

**Date:** 2025-11-29
**Version:** 2.0
**Breaking Changes:** UI redesign, archived features

---

## What Changed

### 🎯 New Features

1. **Static/Dynamic Mode Toggle**
   - **Static Mode:** Preset-based generation with locked parameters (visible but read-only)
   - **Dynamic Mode:** Full manual control over all Gierer-Meinhardt parameters

2. **New Static Mode Presets**
   - **Low Diffusion:** Sharp patterns, defined boundaries (D_b=0.25)
   - **Medium Diffusion:** Balanced waves (D_b=0.35)
   - **High Diffusion:** Soft gradients (D_b=0.50)

### 🗄️ Archived Features

The following features have been **removed from the UI** but preserved in code:

1. **Old Presets** (Stable/Balanced/Active/Chaotic)
   - **Reason:** Replaced by simpler Low/Medium/High Diffusion system
   - **Location:** `archived/ARCHIVED_FEATURES.md`

2. **Dynamic Instability**
   - **Reason:** Redundant with Random Error (less sophisticated)
   - **Location:** `archived/frontend/activator_inhibitor_old.html` (lines 191-236)

3. **Compare with Baseline**
   - **Reason:** Limited analytical value (visual only, no metrics)
   - **Future:** Will be re-implemented with RMSE, SSIM, difference heatmap

### ✅ Preserved Features

These features remain **fully functional**:

- ✅ **Random Error (Biological Perturbation)** - localized pattern disruptions
- ✅ **Show Pattern Evolution** - 4-stage snapshots (25%, 50%, 75%, 100%)
- ✅ **Show Analysis Grid** - 2x2 analytical comparison
- ✅ **Show Biological Heatmap** - activator concentration visualization

---

## User Experience Changes

### Before (Old System)

```
┌─────────────────────────────────┐
│ Preset: [Stable ▼]              │ ← Dropdown with 4 options
│ K: [1.0]                         │
│ t_max: [400]                     │
│ ☑ Dynamic Instability            │ ← Removed
│   - Target: [Both ▼]             │
│   - Strength: [0.01]             │
│ ☑ Random Error                   │
│ ☑ Compare with Baseline          │ ← Removed
│ [Generate]                       │
└─────────────────────────────────┘
```

### After (New System)

```
┌─────────────────────────────────┐
│ [● Static Mode] [○ Dynamic Mode] │ ← NEW: Mode selector
├─────────────────────────────────┤
│ Static Mode:                     │
│   Preset: [Medium Diffusion ▼]  │ ← NEW: Simplified presets
│   s: 0.11 🔒 (locked)            │ ← Visible but read-only
│   D_b: 0.35 🔒 (locked)          │
│   r_a: 0.10 🔒 (locked)          │
│   r_b: 0.18 🔒 (locked)          │
│   K: [1.0] (editable)            │
│   t_max: [400] (editable)        │
│                                  │
│ ☑ Random Error                   │ ← Kept
│ ☑ Pattern Evolution              │ ← Kept
│ ☑ Biological Heatmap             │ ← Kept
│ [Generate]                       │
└─────────────────────────────────┘
```

---

## Technical Changes

### Frontend (JavaScript)

**File:** `static/js/components/texture-generator.js`

#### Old Code (Archived):
```javascript
// Old preset system
params.preset = document.getElementById('preset').value; // stable/balanced/active/chaotic

// Dynamic Instability (removed)
if (enableNoise && enableNoise.checked) {
    params.enable_noise = true;
    params.noise_target = 'Both';
    params.noise_strength = 0.01;
}

// Compare with Baseline (removed)
params.compare_baseline = document.getElementById('compare_with_baseline').checked;
```

#### New Code:
```javascript
// New mode-aware parameter handling
const currentMode = document.body.getAttribute('data-mode'); // 'static' or 'dynamic'

if (currentMode === 'static') {
    // Static Mode: send preset name
    params.preset = document.getElementById('static_preset').value; // low_diffusion/medium_diffusion/high_diffusion
} else {
    // Dynamic Mode: send custom parameters
    params.custom_s = parseFloat(document.getElementById('s_param').value);
    params.custom_D_b = parseFloat(document.getElementById('D_b_param').value);
    params.custom_r_a = parseFloat(document.getElementById('r_a_param').value);
    params.custom_r_b = parseFloat(document.getElementById('r_b_param').value);
}

// Archived features disabled
params.enable_noise = false;
params.compare_baseline = false;
```

### Backend (Python)

**File:** `routes/api.py`

#### Changes:
```python
# Old preset mapping (still works for backward compatibility)
preset_key = data.get('preset')  # e.g., 'stable', 'balanced'
preset_params = SIMULATION_PRESETS.get(preset_key, {})

# NEW: Dynamic Mode custom parameters
if data.get('custom_s') is not None:
    preset_params = {
        's': float(data.get('custom_s', 0.11)),
        'D_b': float(data.get('custom_D_b', 0.35)),
        'r_a': float(data.get('custom_r_a', 0.10)),
        'r_b': float(data.get('custom_r_b', 0.18)),
    }
```

**File:** `config.py`

```python
# Old presets archived
# SIMULATION_PRESETS = {'stable': {...}, 'balanced': {...}, ...}

# NEW: Static Mode presets
STATIC_MODE_PRESETS = {
    'low_diffusion': {'s': 0.11, 'D_b': 0.25, ...},
    'medium_diffusion': {'s': 0.11, 'D_b': 0.35, ...},
    'high_diffusion': {'s': 0.09, 'D_b': 0.50, ...},
}

SIMULATION_PRESETS = STATIC_MODE_PRESETS  # Alias for backward compatibility
```

---

## Backward Compatibility

### API Endpoints

✅ **Fully compatible** - existing API calls still work:

```python
# Old-style request (still works)
POST /calculate
{
    "preset": "stable",  # Maps to low_diffusion
    "K": 1.0,
    "t_max": 400,
    "delta_t": 0.025,
    "color1": "#0000ff",
    "color2": "#ff0000"
}

# New-style request (Static Mode)
POST /calculate
{
    "preset": "medium_diffusion",
    "K": 1.0,
    "t_max": 400,
    "delta_t": 0.025,
    "color1": "#0000ff",
    "color2": "#ff0000"
}

# New-style request (Dynamic Mode)
POST /calculate
{
    "custom_s": 0.12,
    "custom_D_b": 0.30,
    "custom_r_a": 0.10,
    "custom_r_b": 0.18,
    "K": 1.0,
    "t_max": 400,
    "delta_t": 0.025,
    "color1": "#0000ff",
    "color2": "#ff0000"
}
```

### Removed Parameters (Ignored if sent)

These parameters are now **ignored** by the backend:

- `enable_noise` (always set to `false`)
- `noise_target` (ignored)
- `noise_strength` (ignored)
- `compare_baseline` (always set to `false`)

**Impact:** No errors, just silently ignored.

---

## Migration Checklist

### For Users

- [ ] Open application - you'll see the new **Static/Dynamic Mode** toggle
- [ ] Try **Static Mode** - select a preset, parameters are locked
- [ ] Try **Dynamic Mode** - edit all parameters manually
- [ ] **Random Error** still works in both modes
- [ ] **Pattern Evolution** and **Heatmap** still work

### For Developers

- [ ] Review `archived/ARCHIVED_FEATURES.md` for removed code
- [ ] Update any external scripts to use new preset names:
  - `stable` → `low_diffusion` or `medium_diffusion`
  - `balanced` → `medium_diffusion`
  - `active` → `low_diffusion` (for sharp patterns)
  - `chaotic` → *(removed, use Dynamic Mode with custom params)*
- [ ] Remove references to `enable_noise` and `compare_baseline` from external tools

---

## Rollback Procedure

If you need to revert to the old system:

1. **Restore old template:**
   ```bash
   cp archived/frontend/activator_inhibitor_old.html templates/activator_inhibitor.html
   ```

2. **Restore old config presets:**
   ```bash
   git checkout HEAD~1 config.py
   ```

3. **Restore old JavaScript:**
   ```bash
   git checkout HEAD~1 static/js/components/texture-generator.js
   ```

4. **Restart server:**
   ```bash
   python app.py
   ```

---

## Support

- **Issues:** Check `archived/ARCHIVED_FEATURES.md` for removed features
- **Documentation:** See README.md for current feature list
- **Git History:** All changes are versioned and can be reviewed

**Questions?** Open an issue with tag `migration`.
