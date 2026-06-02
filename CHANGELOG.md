# Changelog - Shell Texture Generator

## [2.0.0] - 2025-11-29

### 🎯 Major UI Redesign: Static/Dynamic Mode

#### Added
- **Static/Dynamic Mode Toggle** - Two distinct working modes:
  - **Static Mode:** Preset-based generation with locked parameters (visible but read-only)
  - **Dynamic Mode:** Full manual control over all Gierer-Meinhardt parameters
- **New Static Mode Presets:**
  - `Low Diffusion` (D_b=0.25) - Sharp, well-defined patterns
  - `Medium Diffusion` (D_b=0.35) - Balanced wave-like patterns
  - `High Diffusion` (D_b=0.50) - Soft, smooth gradients
- **Parameter Locking System:**
  - In Static Mode: s, D_b, r_a, r_b displayed but read-only
  - Visual indicators (🔒 icon) show locked state
  - Tooltips explain why parameters are locked
- **Mode-Aware API:**
  - Static Mode sends: `preset` parameter (e.g., "low_diffusion")
  - Dynamic Mode sends: `custom_s`, `custom_D_b`, `custom_r_a`, `custom_r_b`
  - Backend handles both modes transparently

#### Changed
- **Preset System Simplified:**
  - Old presets (Stable/Balanced/Active/Chaotic) → New diffusion-based presets
  - Clearer naming based on primary visual factor (diffusion contrast)
  - Better biological relevance (mimics specific shell species)
- **UI Layout:**
  - Mode selector at top of parameter panel
  - Cleaner separation between basic and advanced features
  - Improved tooltips with mode-specific explanations

#### Deprecated & Archived
- **Old Presets** (Stable/Balanced/Active/Chaotic)
  - Reason: Overlapping behaviors, confusing names
  - Replacement: Low/Medium/High Diffusion
  - Location: `archived/ARCHIVED_FEATURES.md`
- **Dynamic Instability**
  - Reason: Redundant with Random Error, less sophisticated
  - Replacement: Use Random Error (Biological Perturbation)
  - Location: `archived/frontend/activator_inhibitor_old.html`
- **Compare with Baseline**
  - Reason: Limited analytical value (visual only, no metrics)
  - Future: Will be re-implemented with RMSE, SSIM, difference heatmap
  - Location: `archived/ARCHIVED_FEATURES.md`

#### Removed from UI
- ❌ Preset dropdown (Stable/Balanced/Active/Chaotic)
- ❌ "Dynamic Instability" toggle and parameters
- ❌ "Compare with Baseline" checkbox
- ❌ `/set_preset` API endpoint (no longer used by frontend)

#### Preserved Features
- ✅ **Random Error (Biological Perturbation)** - Works in both modes
- ✅ **Show Pattern Evolution (4 stages)** - 25%, 50%, 75%, 100% snapshots
- ✅ **Show Analysis Grid** - 2x2 analytical comparison
- ✅ **Show Biological Heatmap** - Activator concentration visualization
- ✅ All simulation algorithms (Gierer-Meinhardt, Random Error, etc.)

### Technical Changes

#### Frontend (`static/js/components/texture-generator.js`)
```javascript
// NEW: Mode-aware parameter extraction
const currentMode = document.body.getAttribute('data-mode');
if (currentMode === 'static') {
    params.preset = 'low_diffusion';  // Preset name
} else {
    params.custom_s = 0.11;  // Custom parameters
    params.custom_D_b = 0.35;
    // ...
}

// REMOVED: enable_noise, noise_target, noise_strength
// REMOVED: compare_baseline
```

#### Backend (`routes/api.py`)
```python
# NEW: Support for custom parameters from Dynamic Mode
if data.get('custom_s') is not None:
    preset_params = {
        's': float(data.get('custom_s')),
        'D_b': float(data.get('custom_D_b')),
        'r_a': float(data.get('custom_r_a')),
        'r_b': float(data.get('custom_r_b')),
    }

# Archived parameters now ignored (no errors)
enable_noise = False  # Always disabled
compare_baseline = False  # Always disabled
```

#### Configuration (`config.py`)
```python
# NEW: Static Mode presets
STATIC_MODE_PRESETS = {
    'low_diffusion': {...},
    'medium_diffusion': {...},
    'high_diffusion': {...},
}

# Alias for backward compatibility
SIMULATION_PRESETS = STATIC_MODE_PRESETS
```

### Migration Guide

**For Users:**
- Old "Stable" preset → Use "High Diffusion" or "Medium Diffusion"
- Old "Active" preset → Use "Low Diffusion"
- Old "Dynamic Instability" → Use "Random Error" instead
- See `STATIC_DYNAMIC_MODE_GUIDE.md` for detailed usage

**For Developers:**
- Update external scripts to use new preset names
- Remove references to `enable_noise` and `compare_baseline`
- See `MIGRATION_GUIDE.md` for API changes

### Backward Compatibility

✅ **API is backward compatible:**
- Old preset names still work (mapped to new presets)
- Removed parameters are silently ignored (no errors)
- Existing scripts continue to function

### Documentation

- 📖 `STATIC_DYNAMIC_MODE_GUIDE.md` - User guide for new modes
- 📖 `MIGRATION_GUIDE.md` - Technical migration details
- 📖 `archived/ARCHIVED_FEATURES.md` - Documentation of removed features

### Files Changed

**Modified:**
- `templates/activator_inhibitor.html` - Complete UI redesign
- `static/js/components/texture-generator.js` - Mode-aware logic
- `routes/api.py` - Support for custom parameters
- `config.py` - New Static Mode presets

**Added:**
- `STATIC_DYNAMIC_MODE_GUIDE.md` - User guide
- `MIGRATION_GUIDE.md` - Migration documentation
- `CHANGELOG.md` - This file
- `archived/ARCHIVED_FEATURES.md` - Archived feature documentation
- `archived/frontend/activator_inhibitor_old.html` - Old template backup

**Archived:**
- Old preset definitions (in git history)
- Dynamic Instability code (in `archived/frontend/`)
- Compare with Baseline code (in git history)

### Known Issues

- None

### Performance

- **Improved:** Simpler UI = faster initial page load
- **Unchanged:** Simulation performance identical (same algorithms)

### Security

- No security-related changes

---

## [1.0.0] - 2024-11

Initial release with:
- Activator-Inhibitor (Gierer-Meinhardt) model
- Old preset system (Stable/Balanced/Active/Chaotic)
- Dynamic Instability feature
- Random Error (Biological Perturbation)
- Pattern Evolution (4 stages)
- Analysis Grid
- Biological Heatmap

---

## Upgrade Instructions

### From v1.0.0 to v2.0.0:

1. **Backup your current installation:**
   ```bash
   cp templates/activator_inhibitor.html templates/activator_inhibitor_backup.html
   ```

2. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

3. **No database migrations needed** (frontend-only changes)

4. **Restart server:**
   ```bash
   python app.py
   ```

5. **Test new UI:**
   - Open http://localhost:5000
   - Try Static Mode with different presets
   - Try Dynamic Mode with custom parameters
   - Verify Random Error still works

6. **Review documentation:**
   - Read `STATIC_DYNAMIC_MODE_GUIDE.md` for usage
   - Check `MIGRATION_GUIDE.md` for technical details

### Rollback (if needed):

```bash
cp templates/activator_inhibitor_backup.html templates/activator_inhibitor.html
git checkout HEAD~1 config.py routes/api.py static/js/components/texture-generator.js
python app.py
```

---

## Future Plans

### v2.1.0 (Planned)
- **Enhanced Compare with Baseline:**
  - RMSE and SSIM metrics
  - Difference heatmap visualization
  - Interactive overlay slider
  - Quantitative pattern deviation analysis

### v2.2.0 (Planned)
- **Preset Management:**
  - Save custom Dynamic Mode parameters as user presets
  - Import/export preset configurations
  - Share presets via JSON

### v3.0.0 (Planned)
- **Additional Pattern Modes:**
  - Localized Disturbance (from old codebase)
  - Wave Patterns
  - Stripe Patterns
  - Hybrid modes

---

**Questions or issues?** See `MIGRATION_GUIDE.md` or open a GitHub issue.
