import numpy as np
import matplotlib.pyplot as plt
from hashlib import sha256


def encode_text(text, key):
    """Encodes text to numerical values using a key-based offset."""
    key_hash = sha256(key.encode()).hexdigest()
    key_value = int(key_hash[:8], 16) % 256
    return np.array([ord(char) + key_value for char in text])


def decode_text(numbers, key):
    """Decodes numerical values back to text using the same key."""
    key_hash = sha256(key.encode()).hexdigest()
    key_value = int(key_hash[:8], 16) % 256
    return ''.join(chr(int(num - key_value)) for num in numbers)


def map_values_to_sphere(numeric_values, radius):
    """Maps numerical values onto points on a sphere using spherical coordinates."""
    min_val, max_val = np.min(numeric_values), np.max(numeric_values)
    normalized_values = 2 * (numeric_values - min_val) / \
        (max_val - min_val + 1e-9) - 1

    theta = np.arccos(np.clip(normalized_values, -1, 1))
    phi = np.linspace(0, 2 * np.pi, len(numeric_values)
                      )  # Evenly spaced angles

    x = radius * np.sin(theta) * np.cos(phi)
    y = radius * np.sin(theta) * np.sin(phi)
    z = radius * np.cos(theta)
    return x, y, z, min_val, max_val


def project_to_plane(x, y, z, max_range):
    """Projects 3D points on a sphere onto a 2D plane using stereographic projection."""
    epsilon = 1e-9  # Small value to avoid division by zero
    # Clip z to avoid numerical issues
    z = np.clip(z, -1 + epsilon, 1 - epsilon)
    x_proj = np.clip(x / (1 - z), -max_range, max_range)
    y_proj = np.clip(y / (1 - z), -max_range, max_range)
    return x_proj, y_proj


def project_from_plane(x_proj, y_proj):
    """Recovers 3D points on a sphere from a 2D stereographic projection."""
    denominator = x_proj**2 + y_proj**2 + 1
    x = 2 * x_proj / denominator
    y = 2 * y_proj / denominator
    z = (x_proj**2 + y_proj**2 - 1) / denominator
    return x, y, z


def reverse_map_values(z_rec, min_val, max_val):
    """Reverse maps normalized z values back to the original numeric scale."""
    recovered_normalized_values = np.clip(
        z_rec, -1, 1)  # Clip to ensure values are within [-1, 1]
    recovered_numeric_values = (
        recovered_normalized_values + 1) * (max_val - min_val) / 2 + min_val
    recovered_numeric_values = np.round(recovered_numeric_values).astype(int)
    return recovered_numeric_values


def plot_2d_projection(x_proj, y_proj, title="Stereographic Projection"):
    """Visualizes the 2D stereographic projection of points."""
    plt.figure(figsize=(8, 8))
    plt.scatter(x_proj, y_proj, c=np.arange(len(x_proj)), cmap='viridis', s=30)
    plt.axis('equal')
    plt.title(title)
    plt.xlabel("X. Plane")  # Indicate these are plane coordinates
    plt.ylabel("Y. Plane")
    plt.grid(True)
    plt.show()


def plot_3d_points(x, y, z, title):
    """Visualizes 3D points on a sphere."""
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c=np.arange(len(x)), cmap='viridis', s=30)
    ax.set_title(title)
    plt.show()


def validate_inputs(sphere_radius, max_projection_range):
    """Validates the inputs for the main function."""
    if sphere_radius != 1:
        raise ValueError("sphere_radius must be exactly 1. Other values are not supported.")
    if max_projection_range <= 0:
        raise ValueError("max_projection_range must be a positive number (greater than 0).")


def main(sphere_radius=1, max_projection_range=10):
    """Main function to run the encoding, mapping, projection, recovery and decoding process."""

    # Define key and message
    key = "mysecretkey"
    message = "Hello Ralf! How will be the weather today?"
    
    # Validate input
    validate_inputs(sphere_radius, max_projection_range)

    # Encode text
    numeric_values = encode_text(message, key)
    print("Encoded Numeric Values:", numeric_values)

    # Map to sphere
    x, y, z, min_val, max_val = map_values_to_sphere(
        numeric_values, sphere_radius)
    plot_3d_points(x, y, z, "Original Points on Sphere")

    # Perform stereographic projection
    x_proj, y_proj = project_to_plane(x, y, z, max_projection_range)
    plot_2d_projection(x_proj, y_proj)

    # Recover 3D points
    x_rec, y_rec, z_rec = project_from_plane(x_proj, y_proj)
    plot_3d_points(x_rec, y_rec, z_rec, "Recovered 3D Points")

    # Reverse Mapping (from z_rec to original scale)
    recovered_numeric_values = reverse_map_values(z_rec, min_val, max_val)
    print("Recovered Numeric Values:", recovered_numeric_values)

    # Decode text
    decoded_message = decode_text(recovered_numeric_values, key)
    print("Decoded Message:", decoded_message)


if __name__ == "__main__":
    main(sphere_radius=1, max_projection_range=10)
