"""
Noise Generation Utilities for Localized Disturbances

Implements various noise generators for creating spatially-varying
disturbance patterns in reaction-diffusion simulations.
"""
import numpy as np


def generate_perlin_noise_2d(shape, scale=10.0, octaves=4, persistence=0.5, lacunarity=2.0, seed=None):
    """
    Generate 2D Perlin-like noise using gradient noise algorithm.

    This creates smooth, continuous noise with controllable frequency content,
    ideal for simulating natural spatial variations in biological systems.

    Args:
        shape: Tuple (height, width) of output array
        scale: Base scale of noise features (larger = smoother)
        octaves: Number of noise layers to combine (more = more detail)
        persistence: Amplitude decay for each octave (0.5 = half)
        lacunarity: Frequency multiplier for each octave (2.0 = double)
        seed: Random seed for reproducibility

    Returns:
        np.ndarray: 2D array of noise values in range [0, 1]
    """
    if seed is not None:
        np.random.seed(seed)

    height, width = shape
    noise = np.zeros(shape)
    amplitude = 1.0
    frequency = 1.0
    max_value = 0.0

    for octave in range(octaves):
        # Generate gradient grid for this octave
        grid_height = int(np.ceil(height / (scale / frequency))) + 1
        grid_width = int(np.ceil(width / (scale / frequency))) + 1

        # Random gradients at grid points
        gradients_x = np.random.randn(grid_height, grid_width)
        gradients_y = np.random.randn(grid_height, grid_width)

        # Generate noise for this octave
        octave_noise = _interpolated_noise(
            shape, gradients_x, gradients_y, scale / frequency
        )

        noise += octave_noise * amplitude
        max_value += amplitude

        amplitude *= persistence
        frequency *= lacunarity

    # Normalize to [0, 1]
    noise = (noise / max_value + 1.0) / 2.0
    return np.clip(noise, 0, 1)


def _interpolated_noise(shape, gradients_x, gradients_y, scale):
    """Helper function for interpolating gradient noise."""
    height, width = shape
    noise = np.zeros(shape)

    y_coords = np.arange(height) / scale
    x_coords = np.arange(width) / scale

    for i in range(height):
        for j in range(width):
            # Grid cell coordinates
            x0 = int(np.floor(x_coords[j]))
            y0 = int(np.floor(y_coords[i]))
            x1 = x0 + 1
            y1 = y0 + 1

            # Fractional parts
            fx = x_coords[j] - x0
            fy = y_coords[i] - y0

            # Ensure we don't go out of bounds
            x0_idx = min(x0, gradients_x.shape[1] - 1)
            x1_idx = min(x1, gradients_x.shape[1] - 1)
            y0_idx = min(y0, gradients_x.shape[0] - 1)
            y1_idx = min(y1, gradients_x.shape[0] - 1)

            # Dot products with gradients at corners
            dot00 = gradients_x[y0_idx, x0_idx] * fx + gradients_y[y0_idx, x0_idx] * fy
            dot10 = gradients_x[y0_idx, x1_idx] * (fx - 1) + gradients_y[y0_idx, x1_idx] * fy
            dot01 = gradients_x[y1_idx, x0_idx] * fx + gradients_y[y1_idx, x0_idx] * (fy - 1)
            dot11 = gradients_x[y1_idx, x1_idx] * (fx - 1) + gradients_y[y1_idx, x1_idx] * (fy - 1)

            # Smooth interpolation (fade function)
            sx = _fade(fx)
            sy = _fade(fy)

            # Bilinear interpolation
            n0 = _lerp(dot00, dot10, sx)
            n1 = _lerp(dot01, dot11, sx)
            noise[i, j] = _lerp(n0, n1, sy)

    return noise


def _fade(t):
    """Smooth fade function for Perlin noise (6t^5 - 15t^4 + 10t^3)."""
    return t * t * t * (t * (t * 6 - 15) + 10)


def _lerp(a, b, t):
    """Linear interpolation between a and b."""
    return a + t * (b - a)


def generate_block_noise(shape, block_size=20, seed=None):
    """
    Generate blocky noise pattern (simplified version of Perlin).

    Creates constant-value blocks that are randomly assigned values,
    then optionally smoothed. Useful for large-scale disturbances.

    Args:
        shape: Tuple (height, width) of output array
        block_size: Size of each block in pixels
        seed: Random seed for reproducibility

    Returns:
        np.ndarray: 2D array of noise values in range [0, 1]
    """
    if seed is not None:
        np.random.seed(seed)

    height, width = shape

    # Create smaller grid
    grid_height = int(np.ceil(height / block_size))
    grid_width = int(np.ceil(width / block_size))

    # Random values for each block
    grid = np.random.rand(grid_height, grid_width)

    # Expand to full size using nearest-neighbor
    noise = np.zeros(shape)
    for i in range(height):
        for j in range(width):
            grid_i = min(i // block_size, grid_height - 1)
            grid_j = min(j // block_size, grid_width - 1)
            noise[i, j] = grid[grid_i, grid_j]

    return noise


def generate_smooth_block_noise(shape, block_size=20, smoothing=0.3, seed=None):
    """
    Generate smoothed block noise for more natural transitions.

    Args:
        shape: Tuple (height, width) of output array
        block_size: Size of each block in pixels
        smoothing: Smoothing factor (0 = blocky, 1 = very smooth)
        seed: Random seed for reproducibility

    Returns:
        np.ndarray: 2D array of noise values in range [0, 1]
    """
    # Generate base block noise
    noise = generate_block_noise(shape, block_size, seed)

    # Apply Gaussian smoothing
    if smoothing > 0:
        from scipy import ndimage
        sigma = block_size * smoothing
        noise = ndimage.gaussian_filter(noise, sigma=sigma, mode='reflect')
        # Renormalize
        noise = (noise - noise.min()) / (noise.max() - noise.min())

    return noise


def create_disturbance_mask(shape, intensity=0.05, block_size=30,
                           threshold=0.5, noise_type='perlin', seed=None):
    """
    Create a binary or continuous mask for localized disturbances.

    This generates a spatial pattern that indicates where parameter
    modifications should occur in the reaction-diffusion system.

    Args:
        shape: Tuple (height, width) of output array
        intensity: Base intensity of disturbance (will be amplified in masked regions)
        block_size: Spatial scale of disturbance regions
        threshold: Value above which disturbance occurs (for binary mask)
        noise_type: 'perlin', 'block', or 'smooth_block'
        seed: Random seed for reproducibility

    Returns:
        dict: {
            'mask': Binary mask (1 where disturbance occurs, 0 elsewhere),
            'intensity_map': Continuous intensity map [0, 1],
            'strength_multiplier': Local strength multiplier
        }
    """
    if noise_type == 'perlin':
        # Perlin noise with large features
        scale = block_size * 0.5
        noise_map = generate_perlin_noise_2d(
            shape, scale=scale, octaves=3,
            persistence=0.5, lacunarity=2.0, seed=seed
        )
    elif noise_type == 'block':
        noise_map = generate_block_noise(shape, block_size, seed)
    elif noise_type == 'smooth_block':
        noise_map = generate_smooth_block_noise(shape, block_size, smoothing=0.4, seed=seed)
    else:
        raise ValueError(f"Unknown noise_type: {noise_type}")

    # Create binary mask (where disturbances occur)
    mask = (noise_map > threshold).astype(float)

    # Create continuous intensity map (smoother transitions)
    intensity_map = noise_map

    # Create strength multiplier (3x amplification in disturbed regions)
    # In non-disturbed regions: 1x, in disturbed regions: 3x
    strength_multiplier = 1.0 + 2.0 * mask

    return {
        'mask': mask,
        'intensity_map': intensity_map,
        'strength_multiplier': strength_multiplier,
        'noise_map': noise_map
    }


def apply_parameter_disturbance(base_value, disturbance_map,
                                variation_percent=30.0, mode='multiply'):
    """
    Apply localized parameter variations based on disturbance map.

    This modifies reaction-diffusion parameters (r_a, r_b, s) in specific
    regions to create pattern breakdown.

    Args:
        base_value: Base parameter value (scalar or array)
        disturbance_map: 2D array indicating disturbance strength [0, 1]
        variation_percent: Maximum percentage variation (±30% default)
        mode: 'multiply' or 'add'

    Returns:
        np.ndarray: Spatially-varying parameter field
    """
    if mode == 'multiply':
        # ±variation_percent around base value
        # disturbance_map=0.5 → no change
        # disturbance_map=0 → -variation_percent
        # disturbance_map=1 → +variation_percent
        variation_factor = 1.0 + (disturbance_map - 0.5) * 2.0 * (variation_percent / 100.0)
        return base_value * variation_factor
    elif mode == 'add':
        variation = base_value * (variation_percent / 100.0)
        return base_value + (disturbance_map - 0.5) * 2.0 * variation
    else:
        raise ValueError(f"Unknown mode: {mode}")
