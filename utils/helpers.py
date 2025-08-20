"""
Helper Functions and Utilities for Shell Texture Generator

Common utility functions for data validation, color conversion,
and mathematical operations used throughout the application.
"""
import re
from typing import Dict, Any, Tuple
from config import TEXTURE_DEFAULTS

def hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
    """
    Convert HEX color string to RGB tuple with normalized values.
    
    Converts a hexadecimal color representation to RGB values suitable
    for mathematical operations and image processing.
    
    Args:
        hex_color: Color in HEX format (e.g., "#ff0000" or "ff0000")
        
    Returns:
        tuple: RGB values as floats in range [0, 1]
        
    Raises:
        ValueError: If hex_color is not a valid 6-character hex string
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError(f"Invalid HEX color format: {hex_color}")
    
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def validate_hex_color(color: str) -> bool:
    """
    Validate if string represents a valid HEX color code.
    
    Args:
        color: Color string to validate
        
    Returns:
        bool: True if valid HEX color, False otherwise
    """
    if not isinstance(color, str):
        return False
    
    # Remove leading # if present
    color = color.lstrip("#")
    
    # Check if it's exactly 6 characters and all are valid hex digits
    return len(color) == 6 and re.match(r'^[0-9a-fA-F]+$', color) is not None

def validate_texture_params(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate parameters for texture generation algorithms.
    
    Performs comprehensive validation of user input parameters to ensure
    they fall within mathematically valid ranges for the simulation.
    
    Args:
        data: Dictionary containing texture generation parameters
        
    Returns:
        dict: Dictionary with validation results:
            - 'valid': boolean indicating if all parameters are valid
            - 'params': normalized parameter dictionary (if valid)
            - 'error': error message string (if invalid)
    """
    try:
        # Extract and convert parameters with fallback defaults
        K = float(data.get('K', TEXTURE_DEFAULTS['K']))
        t_max = float(data.get('t_max', TEXTURE_DEFAULTS['t_max']))
        delta_t = float(data.get('delta_t', TEXTURE_DEFAULTS['delta_t']))
        color1 = data.get('color1', TEXTURE_DEFAULTS['color1'])
        color2 = data.get('color2', TEXTURE_DEFAULTS['color2'])
        
        # Validate mathematical parameter ranges
        if not (0.1 <= K <= 5.0):
            return {'valid': False, 'error': 'K must be between 0.1 and 5.0'}
        
        if not (1.0 <= t_max <= 10000.0):
            return {'valid': False, 'error': 't_max must be between 1.0 and 10000.0'}
        
        if not (0.001 <= delta_t <= 1.0):
            return {'valid': False, 'error': 'delta_t must be between 0.001 and 1.0'}
        
        # Check numerical stability constraint
        if delta_t > t_max:
            return {'valid': False, 'error': 'delta_t cannot be greater than t_max'}
        
        # Validate color format
        if not validate_hex_color(color1):
            return {'valid': False, 'error': f'Invalid color1 format: {color1}'}
        
        if not validate_hex_color(color2):
            return {'valid': False, 'error': f'Invalid color2 format: {color2}'}
        
        return {
            'valid': True,
            'params': {
                'K': K,
                't_max': t_max,
                'delta_t': delta_t,
                'color1': color1,
                'color2': color2
            }
        }
        
    except (ValueError, TypeError) as e:
        return {'valid': False, 'error': f'Invalid parameter type: {str(e)}'}

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Converts byte count to appropriate unit (B, KB, MB, GB) for display.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Constrain value to specified range.
    
    Mathematical utility function to ensure values stay within bounds.
    
    Args:
        value: Value to constrain
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        float: Clamped value within [min_val, max_val]
    """
    return max(min_val, min(value, max_val))

def normalize_array(arr, min_val: float = 0.0, max_val: float = 1.0) -> 'numpy.ndarray':
    """
    Normalize array values to specified range.
    
    Linear scaling transformation to map array values to target range.
    
    Args:
        arr: Input array to normalize
        min_val: Target minimum value
        max_val: Target maximum value
        
    Returns:
        numpy.ndarray: Normalized array
    """
    import numpy as np
    arr_min, arr_max = np.min(arr), np.max(arr)
    if arr_max == arr_min:
        return np.full_like(arr, min_val)
    
    return min_val + (arr - arr_min) * (max_val - min_val) / (arr_max - arr_min)