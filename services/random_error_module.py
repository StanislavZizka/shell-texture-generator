"""
Random Error Module - Biological Perturbation for Activator-Inhibitor Systems

Implements scientifically grounded random perturbations in reaction-diffusion systems
based on biological observations of pattern formation defects in natural shells.

Mathematical Foundation:
    dA/dt = f(A,B) + R(x,y,t)

    where R(x,y,t) = α · M(x,y) · sin(2πft + φ) · H(t-t₀)H(t₁-t)

    M(x,y) - binary mask of localized regions
    α - perturbation strength (0.01 - 0.05)
    f - frequency of perturbation
    H - Heaviside step function (time windowing)

References:
    - Meinhardt, H. "The Algorithmic Beauty of Sea Shells" (1995)
    - Murray, J.D. "Mathematical Biology II: Spatial Models" (2003)
"""
import numpy as np
from typing import Tuple, Dict, Optional


class RandomErrorModule:
    """
    Biological perturbation module for activator-inhibitor systems.

    Simulates localized, time-limited disruptions in pattern formation
    that occur naturally due to environmental or developmental variations.
    """

    def __init__(self,
                 size: Tuple[int, int],
                 seed: Optional[int] = None):
        """
        Initialize Random Error module.

        Args:
            size: Grid dimensions (height, width)
            seed: Random seed for reproducibility
        """
        self.size = size
        self.rng = np.random.RandomState(seed)

        # Active perturbation state
        self.active_perturbations = []
        self.perturbation_masks = []
        self.perturbation_phases = []
        # Optional per-perturbation drift phases (for mask drift)
        self._drift_phases = []  # list of (phi_x, phi_y)

    def _smooth_profile_1d(self, length: int, passes: int = 4) -> np.ndarray:
        """Create a low-frequency 1D profile from random samples."""

        profile = self.rng.random(max(2, int(length)))
        kernel = np.array([1.0, 4.0, 6.0, 4.0, 1.0], dtype=float)
        kernel /= kernel.sum()

        for _ in range(max(1, int(passes))):
            profile = np.convolve(profile, kernel, mode="same")

        profile = profile - profile.min()
        max_value = float(profile.max())
        if max_value > 0:
            profile = profile / max_value
        return profile

    def _normalize_mask(self, mask: np.ndarray) -> np.ndarray:
        if mask.max() > 0:
            mask = mask / mask.max()
        return np.clip(mask, 0.0, 1.0)

    def _smooth_field_2d(self, field: np.ndarray, passes: int = 1) -> np.ndarray:
        """Apply a lightweight periodic smoothing pass to a 2D field."""

        smoothed = np.asarray(field, dtype=np.float64)
        for _ in range(max(1, int(passes))):
            center = 4.0 * smoothed
            cross = (
                np.roll(smoothed, 1, axis=0)
                + np.roll(smoothed, -1, axis=0)
                + np.roll(smoothed, 1, axis=1)
                + np.roll(smoothed, -1, axis=1)
            )
            diagonals = (
                np.roll(np.roll(smoothed, 1, axis=0), 1, axis=1)
                + np.roll(np.roll(smoothed, 1, axis=0), -1, axis=1)
                + np.roll(np.roll(smoothed, -1, axis=0), 1, axis=1)
                + np.roll(np.roll(smoothed, -1, axis=0), -1, axis=1)
            )
            smoothed = (center + 2.0 * cross + diagonals) / 16.0
        return smoothed

    def _compute_edge_weight(self, field: np.ndarray) -> np.ndarray:
        """Return a smooth edge-aware mask emphasizing field boundaries."""

        field = np.asarray(field, dtype=np.float64)
        field = field - field.min()
        max_value = float(field.max())
        if max_value > 0:
            field = field / max_value
        field = self._smooth_field_2d(field, passes=2)

        grad_x = 0.5 * (np.roll(field, -1, axis=1) - np.roll(field, 1, axis=1))
        grad_y = 0.5 * (np.roll(field, -1, axis=0) - np.roll(field, 1, axis=0))
        grad = np.sqrt(grad_x**2 + grad_y**2)
        grad = self._smooth_field_2d(grad, passes=2)
        grad = self._normalize_mask(grad)

        transition = 1.0 - np.abs(field - 0.5) * 2.0
        transition = np.clip(transition, 0.0, 1.0)
        edge_weight = grad * (0.25 + 0.75 * transition)
        edge_weight = self._smooth_field_2d(edge_weight, passes=2)
        edge_weight = self._normalize_mask(edge_weight)
        edge_weight = np.clip((edge_weight - 0.22) / 0.78, 0.0, 1.0)
        return np.power(edge_weight, 1.08)

    def _compute_contour_response(self, field: np.ndarray) -> np.ndarray:
        """Return a signed contour response concentrated near boundaries."""

        field = np.asarray(field, dtype=np.float64)
        field = field - field.min()
        max_value = float(field.max())
        if max_value > 0:
            field = field / max_value

        smooth = self._smooth_field_2d(field, passes=1)
        contour = field - smooth
        contour = self._smooth_field_2d(contour, passes=1)

        max_abs = float(np.max(np.abs(contour)))
        if max_abs > 0:
            contour = contour / max_abs

        edge_weight = self._compute_edge_weight(field)
        return contour * np.power(edge_weight, 0.85)

    def _generate_spot_mask(
        self,
        num_regions: int = 5,
        region_size: int = 10,
        jitter: float = 0.10,
        micro_noise: float = 0.05,
    ) -> np.ndarray:
        mask = np.zeros(self.size, dtype=float)
        h, w = self.size

        for _ in range(num_regions):
            x0 = self.rng.randint(0, w)
            y0 = self.rng.randint(0, h)
            radius_x = int(region_size * self.rng.uniform(0.7, 1.3))
            radius_y = int(region_size * self.rng.uniform(0.7, 1.3))
            y, x = np.ogrid[:h, :w]
            jitter_x = self.rng.normal(0, radius_x * jitter, (h, w))
            jitter_y = self.rng.normal(0, radius_y * jitter, (h, w))
            dist_x = (x - x0 + jitter_x) / max(radius_x, 1)
            dist_y = (y - y0 + jitter_y) / max(radius_y, 1)
            mask += np.exp(-(dist_x**2 + dist_y**2))

        mask = self._normalize_mask(mask)
        noise = self.rng.normal(0, micro_noise, mask.shape)
        return np.clip(mask * (1 + noise), 0.0, 1.0)

    def _generate_labyrinth_mask(
        self,
        num_regions: int = 5,
        region_size: int = 10,
        jitter: float = 0.10,
        micro_noise: float = 0.05,
    ) -> np.ndarray:
        mask = np.zeros(self.size, dtype=float)
        h, w = self.size
        y, x = np.mgrid[:h, :w]

        for _ in range(max(1, num_regions)):
            x0 = self.rng.uniform(0.15 * w, 0.85 * w)
            y0 = self.rng.uniform(0.15 * h, 0.85 * h)
            angle = self.rng.uniform(-np.pi / 3.0, np.pi / 3.0)
            cos_a = np.cos(angle)
            sin_a = np.sin(angle)
            xr = (x - x0) * cos_a + (y - y0) * sin_a
            yr = -(x - x0) * sin_a + (y - y0) * cos_a
            length = max(8.0, float(region_size) * self.rng.uniform(3.0, 5.0))
            width = max(2.0, float(region_size) * self.rng.uniform(0.35, 0.75))
            bend_amp = width * self.rng.uniform(0.15, 0.35)
            bend_freq = self.rng.uniform(0.8, 1.4) / max(length, 1.0)
            phase = self.rng.uniform(0.0, 2.0 * np.pi)
            bend = bend_amp * np.sin(2.0 * np.pi * bend_freq * xr + phase)
            ribbon = np.exp(-((yr - bend) ** 2) / (2.0 * (width ** 2)))
            ribbon *= np.exp(-(xr ** 2) / (2.0 * (length ** 2)))
            ribbon *= 1.0 + self.rng.normal(0.0, micro_noise * 0.35, self.size)
            mask += np.clip(ribbon, 0.0, None)

        if jitter > 0:
            smooth_x = self._smooth_profile_1d(w, passes=4)
            smooth_y = self._smooth_profile_1d(h, passes=4)
            mask *= 0.75 + 0.25 * np.outer(smooth_y, smooth_x)

        return self._normalize_mask(mask)

    def _generate_stripe_mask(
        self,
        num_regions: int = 5,
        region_size: int = 10,
        jitter: float = 0.10,
        micro_noise: float = 0.05,
        alpha_var: float = 0.20,
        local_y_segments: bool = False,
    ) -> np.ndarray:
        mask = np.zeros(self.size, dtype=float)
        h, w = self.size
        x = np.linspace(0.0, 1.0, w, dtype=float)
        y = np.linspace(0.0, 1.0, h, dtype=float)[:, None]

        base_profile = self._smooth_profile_1d(w, passes=max(4, int(4 + jitter * 8)))
        base_profile = 0.25 + 0.75 * base_profile
        base_profile = np.clip(base_profile, 0.0, 1.0)

        center_slots = np.linspace(0.12, 0.88, max(1, int(num_regions)), dtype=float)
        center_jitter = (self.rng.random(len(center_slots)) - 0.5) * (
            0.10 + 0.06 * float(jitter) + 0.05 * float(micro_noise)
        )
        centers = np.clip(center_slots + center_jitter, 0.06, 0.94)

        x_width_px = max(
            3.0,
            float(region_size) * (0.36 + 0.10 * float(jitter) + 0.04 * float(alpha_var)),
        )
        x_width = x_width_px / max(float(w), 1.0)
        short_height_px = max(
            5.0,
            float(region_size) * (0.78 + 0.18 * float(jitter) + 0.10 * float(alpha_var)),
        )
        long_height_px = max(
            8.0,
            float(region_size) * (1.10 + 0.30 * float(jitter) + 0.12 * float(alpha_var)),
        )
        base_height_px = long_height_px if not local_y_segments else short_height_px
        base_height = base_height_px / max(float(h), 1.0)
        base_strength = np.clip(
            0.55 + 0.25 * float(jitter) + 0.20 * float(alpha_var),
            0.42,
            0.92,
        )
        x_micro = self._smooth_profile_1d(w, passes=2)
        x_micro = 0.85 + 0.15 * (x_micro - 0.5)
        y_micro = self._smooth_profile_1d(h, passes=2)
        y_micro = 0.90 + 0.10 * (y_micro - 0.5)

        segments_per_region = 1 if not local_y_segments else 2
        if local_y_segments and self.rng.random() < 0.55:
            segments_per_region += 1

        for idx, center_x in enumerate(centers):
            x_center = np.clip(center_x, 0.06, 0.94)
            stripe_bias = np.roll(base_profile, int(self.rng.randint(0, max(1, w))))
            stripe_bias = 0.60 + 0.40 * stripe_bias
            x_window = np.exp(-0.5 * ((x - x_center) / max(x_width * (0.88 + 0.18 * self.rng.random()), 1e-6)) ** 2)
            x_window *= stripe_bias
            x_window *= x_micro

            for _ in range(max(1, segments_per_region)):
                y_center = np.clip(self.rng.uniform(0.08, 0.92), 0.06, 0.94)
                segment_height = base_height * (0.82 + 0.34 * self.rng.random())
                if local_y_segments:
                    segment_height *= 0.78 + 0.20 * self.rng.random()
                y_window = np.exp(-0.5 * ((y - y_center) / max(segment_height, 1e-6)) ** 2)
                y_window = np.power(y_window, 1.0 + 0.30 * float(jitter))
                y_window *= y_micro[:, None]

                patch = np.outer(y_window[:, 0], x_window)
                patch = np.clip(patch, 0.0, 1.0)
                mask += patch * base_strength

        if micro_noise > 0:
            fine_x = self._smooth_profile_1d(w, passes=2)
            fine_x = 0.92 + (0.08 * float(micro_noise)) * (fine_x - 0.5)
            mask *= fine_x[None, :]

        return self._normalize_mask(mask)

    def generate_perturbation_mask(self,
                                   num_regions: int = 5,
                                   region_size: int = 10,
                                   jitter: float = 0.10,
                                   micro_noise: float = 0.05,
                                   alpha_var: float = 0.20,
                                   disturbance_kind: str = "generic",
                                   local_y_segments: bool = False) -> np.ndarray:
        """
        Generate irregular, organic mask M(x,y) for localized perturbation regions.

        Creates small, randomly positioned regions with:
        - Gaussian base shape
        - Random noise/jitter on edges (biological irregularity)
        - Variable size and shape for each region

        Args:
            num_regions: Number of perturbation zones (3-10 recommended)
            region_size: Base size of each region in pixels
            jitter: Edge jitter amount (0.10-0.15), preset-specific
            micro_noise: Microstructure noise level (0.05-0.07), preset-specific

        Returns:
            Gradient mask array normalized to [0, 1] with irregular edges
        """
        kind = str(disturbance_kind or "generic").strip().lower()
        if kind in {"stripe", "stripes", "stripe_interrupt", "stripe_interruptions"}:
            return self._generate_stripe_mask(
                num_regions=num_regions,
                region_size=region_size,
                jitter=jitter,
                micro_noise=micro_noise,
                alpha_var=alpha_var,
                local_y_segments=local_y_segments,
            )
        if kind in {"labyrinth", "maze", "corridor"}:
            return self._generate_labyrinth_mask(
                num_regions=num_regions,
                region_size=region_size,
                jitter=jitter,
                micro_noise=micro_noise,
            )
        return self._generate_spot_mask(
            num_regions=num_regions,
            region_size=region_size,
            jitter=jitter,
            micro_noise=micro_noise,
        )

    def compute_perturbation_field(self,
                                   t: float,
                                   alpha: float,
                                   frequency: float,
                                   mask: np.ndarray,
                                   phase: float = 0.0,
                                   alpha_var: float = 0.20) -> np.ndarray:
        """
        Compute R(x,y,t) = α · M(x,y) · sin(2πft + φ) with biological variability.

        Adds micro-variations to amplitude for realistic biological appearance.

        Args:
            t: Current simulation time
            alpha: Base perturbation strength
            frequency: Oscillation frequency
            mask: Spatial mask M(x,y)
            phase: Phase offset φ
            alpha_var: Amplitude variation amount (0.20-0.25), preset-specific

        Returns:
            Perturbation field to add to dA/dt
        """
        # Sinusoidal modulation over time
        temporal_component = np.sin(2 * np.pi * frequency * t + phase)

        # Add biological variability to amplitude
        # This creates micro-fluctuations characteristic of natural systems
        # Use preset-specific alpha_var amount
        alpha_varied = alpha * (1 + alpha_var * self.rng.randn())

        # Spatial modulation with variable amplitude
        R = alpha_varied * mask * temporal_component

        return R

    def trigger_perturbation(self,
                            strength: float = 0.03,
                            duration: int = 30,
                            num_regions: int = 5,
                            region_size: int = 10,
                            frequency: float = 0.05,
                            jitter: float = 0.10,
                            micro_noise: float = 0.05,
                            alpha_var: float = 0.20,
                            drift_x: float = 1.0,
                            drift_y: float = 1.0,
                            drift_frequency: float = 0.002,
                            disturbance_kind: str = "generic",
                            local_y_segments: bool = False) -> int:
        """
        Trigger a new random perturbation event.

        Creates localized perturbation with randomized frequency and phase
        for more natural, non-synchronized oscillations.

        Args:
            strength: Perturbation strength α (0.01 - 0.05)
            duration: How many time steps the perturbation lasts
            num_regions: Number of affected regions (3-10 recommended)
            region_size: Base size of each region in pixels
            frequency: Base oscillation frequency (will be randomized ±20%)
            jitter: Edge jitter amount (0.10-0.15), preset-specific
            micro_noise: Microstructure noise level (0.05-0.07), preset-specific
            alpha_var: Amplitude variation amount (0.20-0.25), preset-specific

        Returns:
            Perturbation ID
        """
        # Generate spatial mask with Gaussian gradients
        # Pass preset-specific biological parameters
        mask = self.generate_perturbation_mask(
            num_regions,
            region_size,
            jitter,
            micro_noise,
            alpha_var=alpha_var,
            disturbance_kind=disturbance_kind,
            local_y_segments=local_y_segments,
        )

        # Random phase offset (different for each perturbation)
        phase = self.rng.uniform(0, 2 * np.pi)

        # Randomize frequency ±20% to avoid synchronization
        frequency_varied = frequency * self.rng.uniform(0.8, 1.2)

        # Store perturbation state
        perturbation_id = len(self.active_perturbations)
        self.active_perturbations.append({
            'id': perturbation_id,
            'start_step': 0,  # Will be set when applied
            'duration': duration,
            'strength': strength,
            'frequency': frequency_varied,  # Use varied frequency
            'remaining_steps': duration,
            'alpha_var': alpha_var,  # Store preset-specific amplitude variation
            'disturbance_kind': str(disturbance_kind or "generic"),
            'local_y_segments': bool(local_y_segments),
            # Drift parameters (in pixels)
            'drift_x': float(drift_x),
            'drift_y': float(drift_y),
            'drift_frequency': float(drift_frequency),
            # Decay state after duration
            'decaying': False
        })
        self.perturbation_masks.append(mask)
        self.perturbation_phases.append(phase)
        # Random drift phases for x/y
        self._drift_phases.append((self.rng.uniform(0, 2*np.pi), self.rng.uniform(0, 2*np.pi)))

        return perturbation_id

    def apply_random_error(self,
                          A: np.ndarray,
                          t: float,
                          step: int,
                          params: Dict) -> np.ndarray:
        """
        Apply active perturbations to activator field A.

        This is the main function called from the simulation loop.
        Computes R(x,y,t) and adds it to dA/dt.

        IMPORTANT: This function also triggers new perturbations probabilistically
        to ensure continuous, dynamic biological defects during simulation.

        Args:
            A: Current activator field
            t: Current simulation time
            step: Current time step number
            params: Perturbation parameters dict containing:
                - strength: base perturbation strength
                - duration: perturbation duration
                - frequency: temporal frequency
                - probability: chance to trigger new perturbation each step
                - num_regions: number of affected regions
                - region_size: size of each region
                - jitter: edge jitter amount (0.10-0.15)
                - micro_noise: microstructure noise level (0.05-0.07)
                - alpha_var: amplitude variation amount (0.20-0.25)

        Returns:
            Perturbation field R(x,y,t) to add to dA/dt
        """
        # Probabilistically trigger new perturbations during simulation
        # This ensures continuous, dynamic biological defects
        if self.should_trigger_new_perturbation(
            step,
            params.get('probability', 0.05),
            min_interval=10  # Allow more frequent perturbations
        ):
            self.trigger_perturbation(
                strength=params.get('strength', 0.06),
                duration=params.get('duration', 30),
                num_regions=params.get('num_regions', 5),
                region_size=params.get('region_size', 10),
                frequency=params.get('frequency', 0.06),
                jitter=params.get('jitter', 0.10),
                micro_noise=params.get('micro_noise', 0.05),
                alpha_var=params.get('alpha_var', 0.20),
                drift_x=params.get('drift_x', 1.2),
                drift_y=params.get('drift_y', 1.0),
                drift_frequency=params.get('drift_frequency', 0.002),
                disturbance_kind=params.get('disturbance_kind', 'generic'),
                local_y_segments=bool(params.get('local_y_segments', False)),
            )

        # If no active perturbations, return zeros
        if not self.active_perturbations:
            return np.zeros_like(A)

        # Accumulate all active perturbations
        R_total = np.zeros_like(A)

        # Process each active perturbation
        perturbations_to_remove = []

        for i, pert in enumerate(self.active_perturbations):
            # Initialize start step if not set
            if pert['start_step'] == 0:
                pert['start_step'] = step

            # Handle active window and post-duration decay
            if pert['remaining_steps'] <= 0:
                # Enter decaying mode if not already
                if not pert.get('decaying', False):
                    pert['decaying'] = True
                # Exponential decay of strength
                pert['strength'] *= 0.9
                # Remove if too weak
                if pert['strength'] < 0.01:
                    perturbations_to_remove.append(i)
                    continue

            # Compute time within perturbation window
            t_local = (step - pert['start_step'])

            # Compute perturbation field with current strength (may be decaying)
            # Use preset-specific alpha_var from perturbation state
            R = self.compute_perturbation_field(
                t=t_local,
                alpha=pert['strength'],
                frequency=pert['frequency'],
                # Apply drift to mask via integer shifts for biological drift
                mask=self._apply_mask_drift(self.perturbation_masks[i], i, step, pert),
                phase=self.perturbation_phases[i],
                alpha_var=pert.get('alpha_var', 0.20)
            )

            R_total += R

            # Decrement remaining steps while in active phase
            if not pert.get('decaying', False):
                pert['remaining_steps'] -= 1

        # Remove expired perturbations
        for idx in reversed(perturbations_to_remove):
            del self.active_perturbations[idx]
            del self.perturbation_masks[idx]
            del self.perturbation_phases[idx]
            del self._drift_phases[idx]

        return R_total

    def should_trigger_new_perturbation(self,
                                       step: int,
                                       probability: float,
                                       min_interval: int = 30) -> bool:
        """
        Decide whether to trigger a new perturbation based on probability.

        Args:
            step: Current time step
            probability: Probability of triggering (0.01 - 0.1)
            min_interval: Minimum steps between perturbations

        Returns:
            True if should trigger new perturbation
        """
        # Check if enough time has passed since last perturbation
        if self.active_perturbations:
            latest_start = max(p['start_step'] for p in self.active_perturbations)
            if step - latest_start < min_interval:
                return False

        # Probabilistic trigger
        return self.rng.random() < probability

    def get_perturbation_map(self) -> np.ndarray:
        """
        Get visualization of currently active perturbation regions.

        Returns:
            2D array showing intensity of perturbations at each location
        """
        if not self.active_perturbations:
            return np.zeros(self.size)

        intensity_map = np.zeros(self.size)

        for i, pert in enumerate(self.active_perturbations):
            # Compute current intensity (constant strength, no decay)
            intensity = pert['strength']
            intensity_map += self.perturbation_masks[i] * intensity

        return intensity_map

    def reset(self):
        """Reset module state, clearing all active perturbations."""
        self.active_perturbations = []
        self.perturbation_masks = []
        self.perturbation_phases = []
        self._drift_phases = []

    def _apply_mask_drift(self, mask: np.ndarray, idx: int, step: int, pert: Dict) -> np.ndarray:
        """Apply slow, sinusoidal drift to a perturbation mask using integer pixel shifts.

        The drift simulates pigment spreading by slowly moving localized defects.

        Args:
            mask: Base mask array
            idx: Perturbation index (to access drift phases)
            step: Current time step
            pert: Perturbation state dict containing drift params

        Returns:
            Drifted mask array (rolled version of base mask)
        """
        if not self._drift_phases:
            return mask
        phi_x, phi_y = self._drift_phases[idx]
        f = float(pert.get('drift_frequency', 0.002))
        amp_x = float(pert.get('drift_x', 1.0))
        amp_y = float(pert.get('drift_y', 1.0))
        # Compute integer pixel shifts
        shift_x = int(round(amp_x * np.sin(2 * np.pi * f * step + phi_x)))
        shift_y = int(round(amp_y * np.cos(2 * np.pi * f * step + phi_y)))
        if shift_x == 0 and shift_y == 0:
            return mask
        return np.roll(mask, shift=(shift_y, shift_x), axis=(0, 1))
def apply_random_error_step(
    module: RandomErrorModule,
    A: np.ndarray,
    t: float,
    step: int,
    params: Dict,
    B: Optional[np.ndarray] = None,
    clamp_min: float = 0.0,
    clamp_max: float = 5.0,
) -> tuple[np.ndarray, Optional[np.ndarray], np.ndarray]:
    """Apply one stochastic disturbance step to activator/inhibitor fields.

    The helper centralizes the shared semantics used by Figure 2.11, 2.12 and
    2.3: the random error is still stochastic and temporally activated, but the
    actual addition to the fields happens during the simulation step rather than
    as a single postprocessing mask.
    """
    perturbation = module.apply_random_error(A, t, step, params)
    kind = str(params.get("disturbance_kind", "generic") or "generic").strip().lower()
    B_next = None
    if kind in {"labyrinth", "maze", "corridor"}:
        raw_perturbation = perturbation
        edge_weight = module._compute_edge_weight(A)
        contour_response = module._compute_contour_response(A)
        edge_strength = np.power(edge_weight, 0.90)
        contour_drive = np.tanh(raw_perturbation * 8.0)
        if B is not None:
            difference_field = A - B
            difference_field = difference_field - float(np.mean(difference_field))
        else:
            difference_field = A - float(np.mean(A))
        difference_drive = np.tanh(difference_field * 3.0)
        epsilon = (0.34 * contour_drive + 0.22 * difference_drive) * contour_response * edge_strength
        epsilon = np.clip(epsilon, -0.24, 0.24)
        A_next = np.clip(A * (1.0 + epsilon), clamp_min, clamp_max)
        perturbation = A_next - A
        if B is not None:
            beta = float(params.get("beta", 0.10))
            B_next = np.clip(B * (1.0 - beta * 0.90 * epsilon), clamp_min, clamp_max)
    else:
        A_next = np.clip(A + perturbation, clamp_min, clamp_max)

    if kind not in {"labyrinth", "maze", "corridor"} and B is not None:
        beta = float(params.get("beta", 0.10))
        B_next = np.clip(B + beta * perturbation, clamp_min, clamp_max)

    return A_next, B_next, perturbation


def run_random_error_disturbance(
    A: np.ndarray,
    params: Dict,
    *,
    B: Optional[np.ndarray] = None,
    seed: Optional[int] = None,
    steps: Optional[int] = None,
    delta_t: float = 1.0,
    clamp_min: float = 0.0,
    clamp_max: float = 5.0,
) -> tuple[np.ndarray, Optional[np.ndarray]]:
    """Run the shared random-error disturbance loop on a field pair.

    This is intentionally lightweight: it does not change the underlying PDE
    model or numerical scheme. It only advances the stochastic disturbance layer
    on top of the provided activator/inhibitor fields.
    """
    if not params.get('enabled', False):
        return A.copy(), None if B is None else B.copy()

    module = RandomErrorModule(size=A.shape, seed=seed)
    current_A = A.copy()
    current_B = None if B is None else B.copy()
    total_steps = max(1, int(steps if steps is not None else params.get('duration', 1)))

    for step in range(total_steps):
        t = step * float(delta_t)
        current_A, current_B, _ = apply_random_error_step(
            module,
            current_A,
            t,
            step,
            params,
            current_B,
            clamp_min=clamp_min,
            clamp_max=clamp_max,
        )

    return current_A, current_B


def create_random_error_params(
    enabled: bool = False,
    strength: float = 0.03,
    duration: int = 30,
    frequency: float = 0.05,
    probability: float = 0.05,
    num_regions: int = 3,
    region_size: int = 10,
    jitter: float = 0.10,
    micro_noise: float = 0.05,
    alpha_var: float = 0.20,
    # New coupling and drift parameters
    beta: float = 0.10,
    drift_x: float = 1.2,
    drift_y: float = 1.0,
    drift_frequency: float = 0.002,
    disturbance_kind: str = "generic",
    local_y_segments: bool = False,
) -> Dict:
    """
    Create standardized parameter dictionary for Random Error.
    These defaults are based on the stable archived version.

    Args:
        enabled: Whether Random Error is active
        strength: Perturbation strength (alpha), typically 0.03-0.05
        duration: Duration in time steps, typically 25-35
        frequency: Oscillation frequency, typically 0.04-0.06
        probability: Trigger probability per step, typically 0.05
        num_regions: Number of perturbation zones, typically 3-5
        region_size: Approximate size of each region in pixels, typically 10
        jitter: Edge jitter amount, typically 0.10-0.15
        micro_noise: Microstructure noise level, typically 0.05-0.07
        alpha_var: Amplitude variation amount, typically 0.20-0.25
        beta: Coupling strength of R into inhibitor B (0.05 - 0.20)
        drift_x: Horizontal drift amplitude in pixels (~1.0 - 1.5)
        drift_y: Vertical drift amplitude in pixels (~0.8 - 1.2)
        drift_frequency: Drift oscillation frequency (~0.002)

    Returns:
        Parameter dictionary
    """
    return {
        'enabled': enabled,
        'strength': float(strength),
        'duration': int(duration),
        'frequency': float(frequency),
        'probability': float(probability),
        'num_regions': int(num_regions),
        'region_size': int(region_size),
        'jitter': float(jitter),
        'micro_noise': float(micro_noise),
        'alpha_var': float(alpha_var),
        'beta': float(beta),
        'drift_x': float(drift_x),
        'drift_y': float(drift_y),
        'drift_frequency': float(drift_frequency),
        'disturbance_kind': str(disturbance_kind or "generic"),
        'local_y_segments': bool(local_y_segments),
    }


# Example usage and testing
if __name__ == '__main__':
    # Test the module
    import matplotlib.pyplot as plt

    print("Testing Random Error Module...")

    # Create module
    size = (128, 128)
    module = RandomErrorModule(size, seed=42)

    # Trigger a perturbation
    params = create_random_error_params(
        enabled=True,
        strength=0.03,
        duration=20,
        num_regions=5
    )

    module.trigger_perturbation(
        strength=params['strength'],
        duration=params['duration'],
        num_regions=params['num_regions'],
        region_size=(params['region_size'], params['region_size'])
    )

    # Simulate time evolution
    A_dummy = np.ones(size) * 0.5

    fig, axes = plt.subplots(2, 4, figsize=(16, 8))

    for i, step in enumerate([0, 5, 10, 15, 20, 25, 30, 35]):
        R = module.apply_random_error(A_dummy, step * 0.5, step, params)

        ax = axes[i // 4, i % 4]
        im = ax.imshow(R, cmap='RdBu_r', vmin=-0.05, vmax=0.05)
        ax.set_title(f'Step {step}')
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046)

    plt.tight_layout()
    plt.savefig('random_error_module_test.png', dpi=150)
    print("Test visualization saved: random_error_module_test.png")

    # Test perturbation map
    pert_map = module.get_perturbation_map()
    print(f"Active perturbations: {len(module.active_perturbations)}")
    print(f"Perturbation map range: [{np.min(pert_map):.4f}, {np.max(pert_map):.4f}]")
