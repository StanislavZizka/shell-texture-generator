"""
Texture Generation Service - Mathematical Pattern Creation

Business logic for generating mathematical textures using reaction-diffusion
algorithms. Implements activator-inhibitor models for natural pattern simulation.
"""
from __future__ import annotations

import numpy as np
import os

# Optional deps: the search harness may import this module from a minimal Python
# (e.g. Blender-bundled Python) that has NumPy but not Flask/Matplotlib/Pillow.
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-GUI backend for serverless deployment
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    matplotlib = None
    plt = None

try:
    from flask import current_app
except Exception:  # pragma: no cover
    class _DummyApp:
        debug = False
    current_app = _DummyApp()


def _debug_enabled() -> bool:
    """Return True only when a Flask app context is active and debug is on."""

    try:
        from flask import has_app_context
    except Exception:  # pragma: no cover
        return False

    if not has_app_context():
        return False

    try:
        return bool(current_app.debug)
    except Exception:  # pragma: no cover
        return False

from config import IMAGES_DIR, SIMULATION_PARAMS, DEFAULT_TEXTURE_SIZE
from config_models import MODEL_212_PARAMS, RANDOM_ERROR_212_STAGES
from core.models import EvaluationResult
from evaluation.metrics_basic import active_area_ratio, image_contrast, image_mean, image_std
from evaluation.metrics_spatial import dominant_orientation_score
from experiments.protocol import build_experiment_id
from services.mode_service import ModeService
from services.experiment_service import ExperimentService
from services.export_service import ExportService
from services.simulation_service import SimulationService
from services.texture_generator_params import build_activator_inhibitor_params
from services.texture_generator_math import calculate_laplacian
from services.texture_generator_snapshots import export_snapshots
from services.texture_generator_random_error_image import create_random_error_image
from services.texture_generator_heatmap import create_biological_heatmap
from utils.helpers import hex_to_rgb
from services.random_error_module import RandomErrorModule, create_random_error_params

class TextureGeneratorService:
    """Service class for generating mathematical textures using various algorithms."""
    
    def __init__(self):
        """Initialize the texture generator service and ensure output directory exists."""
        # Create images directory if it doesn't exist
        os.makedirs(IMAGES_DIR, exist_ok=True)
        self.simulation_service = SimulationService()
        self.export_service = ExportService()
        self.experiment_service = ExperimentService()
        self.mode_service = ModeService(
            simulation_service=self.simulation_service,
            export_service=self.export_service,
            experiment_service=self.experiment_service,
        )
        self.last_mode_result = None

    def _build_activator_inhibitor_params(
        self,
        K: float,
        t_max: float,
        delta_t: float,
        size: int,
        params_override: dict | None,
        preset_name: str,
        color1: str,
        color2: str,
    ):
        """Build the activator-inhibitor simulation dataclass via the shared helper."""

        return build_activator_inhibitor_params(
            K=K,
            t_max=t_max,
            delta_t=delta_t,
            size=size,
            params_override=params_override,
            preset_name=preset_name,
            color1=color1,
            color2=color2,
        )
    
    def generate_activator_inhibitor(self, K: float, t_max: float, delta_t: float,
                                   color1: str, color2: str, size: int = DEFAULT_TEXTURE_SIZE,
                                   params_override: dict | None = None,
                                   random_error_params: dict | None = None,
                                   enable_noise: bool = False,
                                   noise_strength: float = 0.01,
                                   noise_target: str = 'Both',
                                   export_snapshots: bool = False,
                                   show_biological_heatmap: bool = False,
                                   preset_name: str = "custom",
                                   output_filename: str | None = None,
                                   cleanup_prefix: str | None = None) -> tuple[str, str | None]:
        """Generate a reproducible activator-inhibitor texture and metadata."""

        sim_params = self._build_activator_inhibitor_params(
            K=K,
            t_max=t_max,
            delta_t=delta_t,
            size=size,
            params_override=params_override,
            preset_name=preset_name,
            color1=color1,
            color2=color2,
        )

        if _debug_enabled():
            print(
                f"Activator-inhibitor run: preset={sim_params.preset_name}, "
                f"seed={sim_params.random_seed}, size={sim_params.size}, "
                f"steps={int(sim_params.t_max / sim_params.delta_t)}"
            )

        simulation_output = self.simulation_service.run_activator_inhibitor(
            sim_params,
            export_snapshots=export_snapshots,
            random_error_params=random_error_params,
        )

        experiment_id = build_experiment_id(sim_params, color1, color2)
        if cleanup_prefix:
            self.export_service.cleanup_outputs(cleanup_prefix)
        image_path = self.export_service.save_texture(
            simulation_output.A,
            simulation_output.B,
            color1,
            color2,
            output_filename or f"{experiment_id}.png",
        )

        metrics = {
            "mean": image_mean(simulation_output.heatmap),
            "std": image_std(simulation_output.heatmap),
            "contrast": image_contrast(simulation_output.heatmap),
            "active_area_ratio": active_area_ratio(simulation_output.heatmap),
            "dominant_orientation_score": dominant_orientation_score(simulation_output.heatmap),
        }
        evaluation = EvaluationResult(
            metrics=metrics,
            summary=(
                f"Deterministic activator-inhibitor run completed in {simulation_output.steps} steps "
                f"with preset '{sim_params.preset_name}'."
            ),
        )
        record = self.experiment_service.make_record(
            params=sim_params,
            image_path=image_path,
            evaluation=evaluation,
            color1=color1,
            color2=color2,
            notes="Generated through TextureGeneratorService",
        )
        self.experiment_service.persist(record, evaluation)

        if export_snapshots and simulation_output.snapshots:
            self._export_snapshots(simulation_output.snapshots, color1, color2, size)

        if _debug_enabled():
            print(f"Saved experiment record {record.experiment_id}")

        return image_path, simulation_output.heatmap.tolist()

    def generate_stable_periodic_patterns(
        self,
        *,
        stage: int | None = None,
        development_percent: int | None = None,
        stripe_variant: str | None = None,
        params_override: dict | None = None,
        spatial_modulation_override: dict | None = None,
        random_error_params: dict | None = None,
        color1: str,
        color2: str,
        size: int = DEFAULT_TEXTURE_SIZE,
        export_snapshots: bool = False,
    ) -> tuple[str, list[list[float]]]:
        """Generate the stable periodic patterns in space mode."""

        result = self.mode_service.generate_stable_periodic_patterns(
            stage=stage,
            development_percent=development_percent,
            stripe_variant=stripe_variant,
            params_override=params_override,
            spatial_modulation_override=spatial_modulation_override,
            random_error_params=random_error_params,
            color1=color1,
            color2=color2,
            size=size,
            export_snapshots=export_snapshots,
        )
        self.last_mode_result = result
        return result.image_path, result.heatmap_data or []

    def generate_labyrinths(
        self,
        stage: int,
        color1: str,
        color2: str,
        size: int = DEFAULT_TEXTURE_SIZE,
        params_override: dict | None = None,
        random_error_params: dict | None = None,
        export_snapshots: bool = False,
    ) -> str:
        """Generate the labyrinth mode."""

        result = self.mode_service.generate_labyrinths(
            stage=stage,
            color1=color1,
            color2=color2,
            size=size,
            params_override=params_override,
            random_error_params=random_error_params,
            export_snapshots=export_snapshots,
        )
        return result.image_path
    
    def _calculate_laplacian(self, grid: np.ndarray, dx: float = 1.0) -> np.ndarray:
        """
        Calculate discrete Laplacian operator for diffusion simulation.
        
        Uses finite differences with periodic boundary conditions to approximate
        the second spatial derivatives needed for diffusion equations.
        
        Args:
            grid: 2D numpy array representing concentration field
            dx: Spatial step size
            
        Returns:
            np.ndarray: Discrete Laplacian of the input grid
        """
        return calculate_laplacian(grid, dx)
    
    def _create_texture_image(self, A: np.ndarray, B: np.ndarray, 
                            color1: str, color2: str, size: int) -> str:
        """
        Create and save texture image from simulation concentration fields.
        
        Converts numerical simulation results into a visually appealing texture
        by mapping concentration values to color gradients.
        
        Args:
            A: Activator concentration grid
            B: Inhibitor concentration grid
            color1: Base color in HEX format
            color2: Contrast color in HEX format
            size: Image dimensions in pixels
            
        Returns:
            str: Path to saved image file
        """
        # Normalize concentration values to [0, 1] range for color mapping
        a_min, a_max = np.min(A), np.max(A)
        b_min, b_max = np.min(B), np.max(B)
        A_norm = np.clip((A - a_min) / max(a_max - a_min, 1e-12), 0, 1)
        B_norm = np.clip((B - b_min) / max(b_max - b_min, 1e-12), 0, 1)
        
        # Convert HEX colors to RGB values for image creation
        color1_rgb = np.array(hex_to_rgb(color1))
        color2_rgb = np.array(hex_to_rgb(color2))
        
        # Create RGB image by blending colors based on concentrations
        img_data = np.zeros((size, size, 3))
        for i in range(3):
            img_data[:, :, i] = np.clip(color1_rgb[i] * A_norm + color2_rgb[i] * B_norm, 0, 1)
        
        # Save image to static directory for web serving
        output_path = os.path.join(IMAGES_DIR, "activator_inhibitor_texture.png")
        
        try:
            # Use PIL for better Windows compatibility
            from PIL import Image
            img_pil = Image.fromarray((img_data * 255).astype('uint8'))
            img_pil.save(output_path)
            # Skip logging to avoid Windows console issues
        except Exception as e:
            # Skip detailed logging to avoid Windows console issues
            raise

        return output_path

    def _create_biological_heatmap(self, A: np.ndarray, B: np.ndarray, size: int) -> str:
        """
        Create biological heatmap visualization showing activator concentration.

        Uses a colormap (blue › green › yellow › red) to visualize model activity.
        Blue areas = stable/low activity, Red areas = unstable/high activity.

        Args:
            A: Activator concentration grid
            B: Inhibitor concentration grid (optional, for future use)
            size: Image dimensions in pixels

        Returns:
            str: Path to saved heatmap image file
        """
        return create_biological_heatmap(A, B, size)

    def generate_random_error(self, K: float, t_max: float, delta_t: float,
                             color1: str, color2: str, size: int = DEFAULT_TEXTURE_SIZE,
                             noise_target: str = 'Both', noise_type: str = 'initial',
                             noise_strength: float = 0.01, noise_frequency: int = 10,
                             explosion_density: float = 0.1,
                             params_override: dict | None = None) -> str:
        """
        Generate texture using activator-inhibitor model with biologically realistic random errors.

        Simulates biological imperfections in shell patterns with localized pattern breakdown.
        Dynamic noise creates "disturbance patches" where the pattern collapses into irregular
        pigment clusters, mimicking natural growth defects.

        Args:
            K: Spatial scaling applied to diffusion (0.1 - 5.0)
            t_max: Maximum simulation time in arbitrary units
            delta_t: Time step for numerical integration
            color1: Base color in HEX format (activator visualization)
            color2: Contrast color in HEX format (inhibitor visualization)
            size: Texture dimensions in pixels (default from config)
            noise_target: Which field to add noise to ('A', 'B', or 'Both')
            noise_type: When to add noise ('initial' or 'dynamic')
            noise_strength: Amplitude of noise (0.001 - 0.05)
            noise_frequency: How often to add noise in steps (for dynamic noise)
            explosion_density: Probability of explosive bursts (0.0 - 0.2, default 0.1)

        Returns:
            str: Path to generated image file
        """
        from utils.noise_generator import generate_perlin_noise_2d

        # Resolve physical parameters
        _p = dict(SIMULATION_PARAMS)
        if params_override:
            _p.update(params_override)

        # Initialize concentration grids
        A = np.ones((size, size)) * 0.1
        B0 = _p.get('B0', 1.0)
        B = np.ones((size, size)) * B0

        # Add standard noise for pattern formation
        np.random.seed(_p.get('random_seed', 42))
        base_noise = (np.random.rand(size, size) - 0.5) * 0.05
        A += base_noise
        B += (np.random.rand(size, size) - 0.5) * 0.01

        # Generate localized disturbance map for dynamic noise (Perlin-based)
        # This creates "islands of chaos" where noise is amplified
        disturbance_map = None
        if noise_type == 'dynamic':
            # Perlin noise creates smooth, organic disturbance zones
            disturbance_map = generate_perlin_noise_2d(
                shape=(size, size),
                scale=30.0,  # Large features (30-pixel scale)
                octaves=3,
                persistence=0.5,
                lacunarity=2.0,
                seed=_p.get('random_seed', 42) + 1
            )
            # Create local amplification mask (0.6 threshold = ~40% of area affected)
            amplification_mask = (disturbance_map > 0.6).astype(float)
            # Strength multiplier: 1x in normal regions, 5x in disturbance zones
            strength_multiplier = 1.0 + 4.0 * amplification_mask

            affected_area = np.sum(amplification_mask) / amplification_mask.size * 100
            if _debug_enabled():
                print(f"Dynamic disturbance zones: {affected_area:.1f}% of area will have amplified noise")

        # Add initial noise if specified
        if noise_type == 'initial':
            if noise_target in ['A', 'Both']:
                # Spatially-varying initial noise using Perlin
                perlin_noise = generate_perlin_noise_2d(
                    (size, size), scale=20.0, octaves=2, seed=_p.get('random_seed', 42) + 2
                )
                # Convert [0,1] to [-1,1] and scale
                initial_noise_A = (perlin_noise - 0.5) * 2.0 * noise_strength
                A += initial_noise_A
                if _debug_enabled():
                    print(f"Added spatially-correlated initial noise to A: strength={noise_strength}")
            if noise_target in ['B', 'Both']:
                perlin_noise = generate_perlin_noise_2d(
                    (size, size), scale=20.0, octaves=2, seed=_p.get('random_seed', 42) + 3
                )
                initial_noise_B = (perlin_noise - 0.5) * 2.0 * noise_strength * 0.5
                B += initial_noise_B
                if _debug_enabled():
                    print(f"Added spatially-correlated initial noise to B: strength={noise_strength * 0.5}")

        if _debug_enabled():
            print(f"Initial A: min={np.min(A):.6f}, max={np.max(A):.6f}, mean={np.mean(A):.6f}")
            print(f"Initial B: min={np.min(B):.6f}, max={np.max(B):.6f}, mean={np.mean(B):.6f}")
            print(f"Noise: target={noise_target}, type={noise_type}, strength={noise_strength}, freq={noise_frequency}")

        # Get physical parameters
        D_a = _p['D_a']
        D_b = _p['D_b']
        s = _p['s']
        r_a = _p['r_a']
        r_b = _p['r_b']
        b_a = _p['b_a']
        b_b = _p['b_b']
        dx = _p.get('dx', 1.0)

        # Run simulation
        steps = int(t_max / delta_t)
        if _debug_enabled():
            print(f"K={K}, delta_t={delta_t}, t_max={t_max}, steps={steps}")

        # Stability limit
        max_D = max(D_a, D_b)
        if K * max_D > 0:
            max_dt_diff = (dx * dx) / (4.0 * K * max_D)
            safe_dt = 0.8 * max_dt_diff
        else:
            safe_dt = delta_t
        substeps = max(1, int(np.ceil(delta_t / max(safe_dt, 1e-12))))
        dt_sub = delta_t / substeps

        s_current = s
        runaway_counter = 0

        # Track explosive zones for visualization
        explosion_count = 0

        for step in range(steps):
            # Add dynamic noise at specified frequency with localized amplification
            if noise_type == 'dynamic' and step > 0 and step % noise_frequency == 0:
                # 1. FINE-GRAINED PERLIN NOISE (continuous fluctuations)
                perlin_fine = generate_perlin_noise_2d(
                    (size, size), scale=15.0, octaves=2,
                    seed=_p.get('random_seed', 42) + step
                )
                # Convert to noise field: [-noise_strength, +noise_strength]
                noise_field = (perlin_fine - 0.5) * 2.0 * noise_strength

                if noise_target in ['A', 'Both']:
                    # Apply gentle multiplicative noise everywhere
                    A += A * noise_field

                if noise_target in ['B', 'Both']:
                    # Inhibitor gets slightly weaker noise
                    B += B * noise_field * 0.8

                # 2. LOCALIZED DISTURBANCE ZONES (where pattern breaks down)
                if disturbance_map is not None and amplification_mask is not None:
                    if noise_target in ['A', 'Both']:
                        # In disturbance zones: stronger multiplicative noise
                        disturbance_noise_A = amplification_mask * A * np.random.uniform(0.5, 1.5, (size, size)) * noise_strength * 2.0
                        A += disturbance_noise_A

                    if noise_target in ['B', 'Both']:
                        disturbance_noise_B = amplification_mask * B * np.random.uniform(0.3, 1.0, (size, size)) * noise_strength * 1.5
                        B += disturbance_noise_B

            # 3. EXPLOSIVE BURSTS (guaranteed pigment explosions)
            # Create deterministic explosion schedule based on explosion_density
            # explosion_density 0.1 = 10% of total steps will have explosions
            if noise_type == 'dynamic' and step > 0:
                # Calculate explosion interval to achieve desired density
                # e.g., density=0.1, steps=120 â†’ explosion every ~12 steps
                explosion_interval = max(5, int(1.0 / max(explosion_density, 0.01)))

                if step % explosion_interval == 0:
                    # Create 1-2 explosive zones (guaranteed)
                    num_explosions = np.random.randint(1, 3)
                    for _ in range(num_explosions):
                        # Random position and radius
                        rx, ry = np.random.randint(0, size, 2)
                        radius = np.random.randint(5, 12)  # Larger for visibility

                        # Create explosion mask (circular region)
                        y_grid, x_grid = np.ogrid[:size, :size]
                        explosion_mask = ((x_grid - rx)**2 + (y_grid - ry)**2 <= radius**2).astype(float)

                        if noise_target in ['A', 'Both']:
                            # Explosive amplification: 1.5x-3x (visible but not destructive)
                            explosion_factor = np.random.uniform(1.5, 3.0)
                            A += explosion_mask * A * explosion_factor

                        if noise_target in ['B', 'Both']:
                            explosion_factor_B = np.random.uniform(1.2, 2.0)
                            B += explosion_mask * B * explosion_factor_B

                        explosion_count += 1

            # Perform substeps with consistent dt_sub integration
            for __ in range(substeps):
                A_laplace = self._calculate_laplacian(A, dx)
                B_laplace = self._calculate_laplacian(B, dx)
                B_safe = np.maximum(B, 1e-10)
                dA_dt = s_current * (A**2 / B_safe + b_a) - r_a * A + (K * D_a) * A_laplace
                dB_dt = s_current * A**2 - r_b * B + (K * D_b) * B_laplace + b_b
                A += dt_sub * dA_dt
                B += dt_sub * dB_dt

            # Enforce bounds
            A = np.clip(A, 0.0, 2.0)
            B = np.clip(B, 0.0, 2.0)

            # Adaptive stabilization
            if np.max(A) > 2.0 or np.max(B) > 2.0:
                runaway_counter += 1
            else:
                runaway_counter = 0
            if runaway_counter >= 3:
                s_current *= 0.9
                runaway_counter = 0

            # Log updates
            if step % 10 == 0 and _debug_enabled():
                print(f"Step {step}: A [{np.min(A):.3f}, {np.max(A):.3f}], B [{np.min(B):.3f}, {np.max(B):.3f}]")

        # Summary of dynamic instability effects
        if noise_type == 'dynamic' and _debug_enabled():
            print(f"\n{'='*70}")
            print(f"Dynamic Instability Summary:")
            print(f"  Total explosive bursts: {explosion_count}")
            print(f"  Expected visible disruptions in final texture")
            print(f"{'='*70}\n")

        # Generate image with descriptive filename
        image_path = self._create_random_error_image(A, B, color1, color2, size, noise_target, noise_type)
        return image_path

    def _create_random_error_image(self, A: np.ndarray, B: np.ndarray,
                                  color1: str, color2: str, size: int,
                                  noise_target: str, noise_type: str) -> str:
        """Create and save random error texture with descriptive filename."""
        return create_random_error_image(A, B, color1, color2, size, noise_target, noise_type)

    def generate_localized_disturbance(self, K: float, t_max: float, delta_t: float,
                                      color1: str, color2: str, size: int = DEFAULT_TEXTURE_SIZE,
                                      intensity: float = 0.05, block_size: int = 30,
                                      target: str = 'both', variation_percent: float = 30.0,
                                      noise_type_disturbance: str = 'perlin',
                                      params_override: dict | None = None) -> str:
        """
        Generate texture with localized pattern stability breakdown.

        Implements the localized disturbance mechanism from "Algorithmic Beauty
        of Sea Shells" chapter 1.8. Creates regions where parameters are locally
        modified, causing pattern breakdown and pigment cluster formation.

        Args:
            K: Spatial scaling (0.1 - 5.0)
            t_max: Maximum simulation time
            delta_t: Time step
            color1: Base color (hex)
            color2: Contrast color (hex)
            size: Texture dimensions in pixels
            intensity: Base noise intensity (0.03 - 0.07)
            block_size: Size of disturbance regions (20 - 40 pixels)
            target: Which to disturb ('activator', 'inhibitor', 'both', 'parameters')
            variation_percent: Parameter variation in disturbed regions (Â±30% default)
            noise_type_disturbance: 'perlin', 'block', or 'smooth_block'
            params_override: Override simulation parameters

        Returns:
            str: Path to generated image
        """
        from utils.noise_generator import create_disturbance_mask, apply_parameter_disturbance

        # Resolve parameters
        _p = dict(SIMULATION_PARAMS)
        if params_override:
            _p.update(params_override)

        # Initialize fields
        A = np.ones((size, size)) * 0.1
        B0 = _p.get('B0', 1.0)
        B = np.ones((size, size)) * B0

        # Standard initialization noise
        np.random.seed(_p.get('random_seed', 42))
        base_noise = (np.random.rand(size, size) - 0.5) * 0.05
        A += base_noise
        B += (np.random.rand(size, size) - 0.5) * 0.01

        # Create localized disturbance mask
        disturbance = create_disturbance_mask(
            shape=(size, size),
            intensity=intensity,
            block_size=block_size,
            threshold=0.6,  # Higher threshold = fewer, more distinct regions
            noise_type=noise_type_disturbance,
            seed=_p.get('random_seed', 42) + 1
        )

        mask = disturbance['mask']
        intensity_map = disturbance['intensity_map']
        strength_mult = disturbance['strength_multiplier']

        if _debug_enabled():
            print(f"Localized disturbance: {np.sum(mask) / mask.size * 100:.1f}% of area affected")
            print(f"Disturbance params: block_size={block_size}, variation=Â±{variation_percent}%")

        # Get base parameters
        D_a = _p['D_a']
        D_b = _p['D_b']
        s_base = _p['s']
        r_a_base = _p['r_a']
        r_b_base = _p['r_b']
        b_a = _p['b_a']
        b_b = _p['b_b']
        dx = _p.get('dx', 1.0)

        # Create spatially-varying parameters if targeting parameters
        if target == 'parameters':
            # Vary s, r_a, r_b based on disturbance map
            s_field = apply_parameter_disturbance(s_base, intensity_map, variation_percent)
            r_a_field = apply_parameter_disturbance(r_a_base, intensity_map, variation_percent)
            r_b_field = apply_parameter_disturbance(r_b_base, intensity_map, variation_percent)
            if _debug_enabled():
                print(f"Parameter fields: s [{np.min(s_field):.4f}, {np.max(s_field):.4f}]")
                print(f"                  r_a [{np.min(r_a_field):.4f}, {np.max(r_a_field):.4f}]")
                print(f"                  r_b [{np.min(r_b_field):.4f}, {np.max(r_b_field):.4f}]")
        else:
            s_field = s_base
            r_a_field = r_a_base
            r_b_field = r_b_base

        # Run simulation
        steps = int(t_max / delta_t)
        if _debug_enabled():
            print(f"K={K}, delta_t={delta_t}, t_max={t_max}, steps={steps}")

        # Stability check
        max_D = max(D_a, D_b)
        if K * max_D > 0:
            max_dt_diff = (dx * dx) / (4.0 * K * max_D)
            safe_dt = 0.8 * max_dt_diff
        else:
            safe_dt = delta_t
        substeps = max(1, int(np.ceil(delta_t / max(safe_dt, 1e-12))))
        dt_sub = delta_t / substeps

        s_current = s_field if target == 'parameters' else s_base
        runaway_counter = 0

        for step in range(steps):
            # Apply enhanced noise in disturbed regions every N steps
            if step > 0 and step % 5 == 0:
                if target in ['activator', 'both']:
                    # 3x amplified noise in disturbed regions
                    local_noise = np.random.normal(0, intensity, A.shape)
                    A += local_noise * strength_mult
                if target in ['inhibitor', 'both']:
                    local_noise = np.random.normal(0, intensity, B.shape)
                    B += local_noise * strength_mult

            # Substeps with consistent dt_sub integration
            for __ in range(substeps):
                A_laplace = self._calculate_laplacian(A, dx)
                B_laplace = self._calculate_laplacian(B, dx)
                B_safe = np.maximum(B, 1e-10)

                # Use spatially-varying parameters if applicable
                if target == 'parameters':
                    dA_dt = s_field * (A**2 / B_safe + b_a) - r_a_field * A + (K * D_a) * A_laplace
                    dB_dt = s_field * A**2 - r_b_field * B + (K * D_b) * B_laplace + b_b
                else:
                    dA_dt = s_current * (A**2 / B_safe + b_a) - r_a_base * A + (K * D_a) * A_laplace
                    dB_dt = s_current * A**2 - r_b_base * B + (K * D_b) * B_laplace + b_b

                A += dt_sub * dA_dt
                B += dt_sub * dB_dt

            # Bounds
            A = np.clip(A, 0.0, 2.0)
            B = np.clip(B, 0.0, 2.0)

            # Stabilization
            if np.max(A) > 2.0 or np.max(B) > 2.0:
                runaway_counter += 1
            else:
                runaway_counter = 0
            if runaway_counter >= 3:
                if target != 'parameters':
                    s_current *= 0.9
                runaway_counter = 0

            # Logging
            if step % 10 == 0 and _debug_enabled():
                print(f"Step {step}: A [{np.min(A):.3f}, {np.max(A):.3f}], B [{np.min(B):.3f}, {np.max(B):.3f}]")

        # Generate image
        image_path = self._create_localized_image(A, B, color1, color2, size, target, block_size)
        return image_path

    def _create_localized_image(self, A: np.ndarray, B: np.ndarray,
                               color1: str, color2: str, size: int,
                               target: str, block_size: int) -> str:
        """Create and save localized disturbance texture."""
        # Normalize
        a_min, a_max = np.min(A), np.max(A)
        b_min, b_max = np.min(B), np.max(B)
        A_norm = np.clip((A - a_min) / max(a_max - a_min, 1e-12), 0, 1)
        B_norm = np.clip((B - b_min) / max(b_max - b_min, 1e-12), 0, 1)

        # Convert colors
        color1_rgb = np.array(hex_to_rgb(color1))
        color2_rgb = np.array(hex_to_rgb(color2))

        # Create image
        img_data = np.zeros((size, size, 3))
        for i in range(3):
            img_data[:, :, i] = np.clip(color1_rgb[i] * A_norm + color2_rgb[i] * B_norm, 0, 1)

        # Filename
        filename = f"localized_disturbance_{target}_block{block_size}.png"
        output_path = os.path.join(IMAGES_DIR, filename)

        try:
            from PIL import Image
            img_pil = Image.fromarray((img_data * 255).astype('uint8'))
            img_pil.save(output_path)
        except Exception as e:
            raise

        return output_path

    def generate_with_biological_perturbation(self, K: float, t_max: float, delta_t: float,
                                              color1: str, color2: str, size: int = DEFAULT_TEXTURE_SIZE,
                                              params_override: dict | None = None,
                                              random_error_params: dict | None = None,
                                              export_snapshots: bool = False) -> str:
        """
        Generate texture with Random Error using a new, stable simulation core
        based on a known-working reference implementation.
        """
        # 1. Resolve Parameters from config and overrides
        _p = dict(SIMULATION_PARAMS)
        if params_override:
            _p.update(params_override)

        # Map parameters to variable names used in the new stable core
        s = _p['s']
        r_a = _p['r_a']
        r_b = _p['r_b']
        b_a = _p['b_a']
        b_b = _p['b_b']
        dx = _p.get('dx', 1.0)
        D_a = _p['D_a']
        D_b = _p['D_b']
        
        # Apply the K factor, which scales diffusion
        D_a *= K
        D_b *= K

        if _debug_enabled():
            print("--- Using New Stable Simulation Core ---")
            print(f"Parameters: s={s:.2f}, r_a={r_a:.2f}, r_b={r_b:.2f}, D_a={D_a:.4f}, D_b={D_b:.4f}")

        # 2. Initialize Grids
        np.random.seed(_p.get('random_seed', 42))
        A = np.ones((size, size)) * 0.1
        B = np.ones((size, size)) * 1.0
        A += (np.random.rand(size, size) - 0.5) * 0.05
        B += (np.random.rand(size, size) - 0.5) * 0.01

        # 3. Initialize Random Error Module
        re_module = None
        re_params = random_error_params or create_random_error_params()
        random_error_enabled = re_params.get('enabled', False)
        if random_error_enabled:
            re_module = RandomErrorModule(size=(size, size), seed=_p.get('random_seed', 42))
            if _debug_enabled():
                print("Random Error is ENABLED.")

        # 4. Main Simulation Loop
        print(f"SKUTEÄŚNĂ‰ PARAMS: s={s}, r_a={r_a}, r_b={r_b}, D_a={D_a}, D_b={D_b}, b_a={b_a}, b_b={b_b}, K={K}, delta_t={delta_t}, t_max={t_max}")
        print(f"INIT: A mean={np.mean(A):.6f}, min={np.min(A):.6f}, max={np.max(A):.6f}")
        print(f"INIT: B mean={np.mean(B):.6f}, min={np.min(B):.6f}, max={np.max(B):.6f}")
        steps = int(t_max / delta_t)
        beta_couple = (re_params.get('beta') if re_params else None)
        if beta_couple is None:
            beta_couple = 0.10
        for step in range(steps):
            # Calculate Laplacian using periodic boundary conditions
            lap_A = self._calculate_laplacian(A, dx)
            lap_B = self._calculate_laplacian(B, dx)

            # Prevent division by zero in the reaction term
            B_safe = np.maximum(B, 1e-10)

            # Core Gierer-Meinhardt equations
            dA_dt = D_a * lap_A + s * (A**2 / B_safe) - r_a * A + (s * b_a)
            dB_dt = D_b * lap_B + s * (A**2) - r_b * B + b_b

            # Perform time integration (main update)
            A += delta_t * dA_dt
            B += delta_t * dB_dt

            # Apply Random Error AFTER diffusion but BEFORE clipping
            # This ensures local defects remain visible and aren't smoothed out
            if random_error_enabled and re_module:
                t = step * delta_t
                R = re_module.apply_random_error(A, t, step, re_params)
                if R is not None:
                    # Add perturbation directly to concentration fields
                    A += R
                    B += beta_couple * R

                    if step % 50 == 0 and _debug_enabled():
                        print(f"DEBUG Step {step}: R mean={np.mean(R):.6f}, max={np.max(R):.6f}, min={np.min(R):.6f}")

            # Soft clipping to maintain bounds
            np.clip(A, 0, 5, out=A)
            np.clip(B, 0, 5, out=B)

        # 5. Create and Save the Final Image
        filename = "stable_gm_output.png"
        if random_error_enabled:
            # Create a more descriptive filename for perturbed outputs
            filename = f"biological_perturbation_s{re_params['strength']:.4f}_d{re_params['duration']}.png"
        
        # Note: The _create_texture_image and _create_biological_perturbation_image methods
        # need to be updated to accept a dynamic filename. This will be done in a subsequent step.
        image_path = self._create_biological_perturbation_image(A, B, color1, color2, size,
                                                                random_error_enabled, 0) # Pass dummy count

        return image_path

    def _create_biological_perturbation_image(self, A: np.ndarray, B: np.ndarray,
                                             color1: str, color2: str, size: int,
                                             random_error_enabled: bool = False,
                                             perturbation_count: int = 0,
                                             filename: str | None = None) -> str:
        """Create and save texture image from biological perturbation simulation."""
        # Normalize
        a_min, a_max = np.min(A), np.max(A)
        b_min, b_max = np.min(B), np.max(B)
        A_norm = np.clip((A - a_min) / max(a_max - a_min, 1e-12), 0, 1)
        B_norm = np.clip((B - b_min) / max(b_max - b_min, 1e-12), 0, 1)

        # Convert colors
        color1_rgb = np.array(hex_to_rgb(color1))
        color2_rgb = np.array(hex_to_rgb(color2))

        # Create RGB image
        img_data = np.zeros((size, size, 3))
        for i in range(3):
            img_data[:, :, i] = np.clip(color1_rgb[i] * A_norm + color2_rgb[i] * B_norm, 0, 1)

        # Filename logic
        if filename is None:
            if random_error_enabled:
                filename = f"biological_perturbation_n{perturbation_count}.png"
            else:
                filename = "activator_inhibitor_texture.png"
        
        output_path = os.path.join(IMAGES_DIR, filename)

        try:
            from PIL import Image
            img_pil = Image.fromarray((img_data * 255).astype('uint8'))
            img_pil.save(output_path)
        except Exception as e:
            raise

        return output_path

    def _export_snapshots(self, snapshots, color1: str, color2: str, size: int):
        """Export intermediate simulation snapshots via the shared helper."""
        return export_snapshots(snapshots, color1, color2, size)

    def generate_activator_inhibitor_212(self, stage: int, color1: str, color2: str,
                                         size: int = DEFAULT_TEXTURE_SIZE,
                                         random_error_params: dict | None = None) -> str:
        from services.texture_generator_fig212 import generate_activator_inhibitor_212 as _generate_212

        return _generate_212(self, stage, color1, color2, size=size, random_error_params=random_error_params)

