"""
Texture Generation Service - Mathematical Pattern Creation

Business logic for generating mathematical textures using reaction-diffusion
algorithms. Implements activator-inhibitor models for natural pattern simulation.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for serverless deployment
import matplotlib.pyplot as plt
import os
from config import IMAGES_DIR, SIMULATION_PARAMS, DEFAULT_TEXTURE_SIZE
from utils.helpers import hex_to_rgb

class TextureGeneratorService:
    """Service class for generating mathematical textures using various algorithms."""
    
    def __init__(self):
        """Initialize the texture generator service and ensure output directory exists."""
        # Create images directory if it doesn't exist
        os.makedirs(IMAGES_DIR, exist_ok=True)
    
    def generate_activator_inhibitor(self, K: float, t_max: float, delta_t: float, 
                                   color1: str, color2: str, size: int = DEFAULT_TEXTURE_SIZE) -> str:
        """
        Generate texture using activator-inhibitor reaction-diffusion model.
        
        This implements the Gray-Scott model for reaction-diffusion systems that
        create patterns similar to those found on animal shells and other natural surfaces.
        
        Args:
            K: Model constant controlling reaction rate (0.1 - 5.0)
            t_max: Maximum simulation time in arbitrary units
            delta_t: Time step for numerical integration
            color1: Base color in HEX format (activator visualization)
            color2: Contrast color in HEX format (inhibitor visualization)
            size: Texture dimensions in pixels (default from config)
            
        Returns:
            str: Path to generated image file
        """
        # Initialize concentration grids with equilibrium values
        A = np.ones((size, size)) * 0.5  # Activator concentration
        B = np.ones((size, size)) * 0.25  # Inhibitor concentration
        
        # Add random noise as initial perturbation for pattern formation
        np.random.seed(SIMULATION_PARAMS['random_seed'])
        noise = (np.random.rand(size, size) - 0.5) * 0.1
        A += noise
        B += noise
        
        # Get physical parameters from configuration
        D_a = SIMULATION_PARAMS['D_a']  # Activator diffusion rate
        D_b = SIMULATION_PARAMS['D_b']  # Inhibitor diffusion rate
        feed_rate = SIMULATION_PARAMS['feed_rate']  # Feed rate parameter
        kill_rate = SIMULATION_PARAMS['kill_rate']  # Kill rate parameter
        
        # Run numerical simulation
        steps = int(t_max / delta_t)
        for step in range(steps):
            # Calculate spatial derivatives using discrete Laplacian operator
            A_laplace = self._calculate_laplacian(A)
            B_laplace = self._calculate_laplacian(B)
            
            # Apply Gray-Scott reaction-diffusion equations
            reaction = A * B**2  # Autocatalytic reaction term
            A += delta_t * (D_a * A_laplace - reaction + feed_rate * (1 - A))
            B += delta_t * (D_b * B_laplace + reaction - (kill_rate + feed_rate) * B)
            
            # Log simulation progress for monitoring
            if step % 100 == 0:
                print(f"Simulation step {step}/{steps}: A range=[{np.min(A):.4f}, {np.max(A):.4f}], "
                      f"B range=[{np.min(B):.4f}, {np.max(B):.4f}]")
        
        # Generate final texture image from simulation results
        image_path = self._create_texture_image(A, B, color1, color2, size)
        return image_path
    
    def _calculate_laplacian(self, grid: np.ndarray) -> np.ndarray:
        """
        Calculate discrete Laplacian operator for diffusion simulation.
        
        Uses finite differences with periodic boundary conditions to approximate
        the second spatial derivatives needed for diffusion equations.
        
        Args:
            grid: 2D numpy array representing concentration field
            
        Returns:
            np.ndarray: Discrete Laplacian of the input grid
        """
        return (
            np.roll(grid, 1, axis=0) + np.roll(grid, -1, axis=0) +
            np.roll(grid, 1, axis=1) + np.roll(grid, -1, axis=1) - 4 * grid
        )
    
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
        A_norm = np.clip((A - np.min(A)) / (np.max(A) - np.min(A)), 0, 1)
        B_norm = np.clip((B - np.min(B)) / (np.max(B) - np.min(B)), 0, 1)
        
        # Convert HEX colors to RGB values for image creation
        color1_rgb = np.array(hex_to_rgb(color1))
        color2_rgb = np.array(hex_to_rgb(color2))
        
        # Create RGB image by blending colors based on concentrations
        img_data = np.zeros((size, size, 3))
        for i in range(3):
            img_data[:, :, i] = np.clip(color1_rgb[i] * A_norm + color2_rgb[i] * B_norm, 0, 1)
        
        # Save image to static directory for web serving
        output_path = os.path.join(IMAGES_DIR, "activator_inhibitor_texture.png")
        plt.imsave(output_path, img_data)
        
        return output_path