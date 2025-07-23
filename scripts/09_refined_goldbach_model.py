
import csv
import os
import numpy as np
import matplotlib.pyplot as plt

def moving_average(data, window_size):
    """Calculates the moving average of a list of data."""
    if window_size <= 0:
        raise ValueError("Window size must be positive.")
    if window_size > len(data):
        return np.full_like(data, np.mean(data)) # Return mean if window is too large

    # Pad the data to handle edges, or use a 'valid' mode for smaller output
    # For simplicity, we'll use 'valid' mode, which means the output will be shorter
    # Let's use 'same' mode by padding
    padded_data = np.pad(data, (window_size // 2, window_size - 1 - window_size // 2), mode='edge')
    return np.convolve(padded_data, np.ones(window_size)/window_size, mode='valid')

def main():
    """Calculates and plots the refined Goldbach model."""
    analysis_filename = os.path.join(os.path.dirname(__file__), '..', 'data', 'goldbach_full_analysis.csv')
    plot_filename = os.path.join(os.path.dirname(__file__), '..', 'plots', '08_g_n_refined_model.png')

    n_values, g_n_real_values, g_n_asymptotic_values, delta_values = [], [], [], []
    print(f"Reading data from {analysis_filename}...")
    with open(analysis_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            n_values.append(int(row['N']))
            g_n_real_values.append(float(row['g(N)_real']))
            g_n_asymptotic_values.append(float(row['g(N)_asymptotic']))
            delta_values.append(float(row['Delta(N)']))
    print("Data reading complete.")

    # --- Smooth Delta(N) ---
    window_size = 500 # Adjust this value to control smoothing
    print(f"Smoothing Delta(N) with a moving average window of {window_size}...")
    delta_smoothed = moving_average(delta_values, window_size)
    print("Smoothing complete.")

    # --- Calculate Refined Model ---
    print("Calculating refined model...")
    g_n_refined_values = np.array(g_n_asymptotic_values) + np.array(delta_smoothed)
    print("Refined model calculation complete.")

    # --- Plotting ---
    print(f"Generating plot and saving to {plot_filename}...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(15, 10))

    # Plot real data
    ax.plot(n_values, g_n_real_values, 'o', markersize=1, color='cyan', alpha=0.6, label='Datos Reales g(N)')
    
    # Plot asymptotic approximation
    ax.plot(n_values, g_n_asymptotic_values, '-', color='magenta', linewidth=2, label='Aproximación Asintótica (Hardy-Littlewood)')

    # Plot refined model
    ax.plot(n_values, g_n_refined_values, '-', color='lime', linewidth=2, label='Modelo Refinado')

    ax.set_title('g(N) Real vs. Aproximación Asintótica vs. Modelo Refinado', fontsize=20, color='white')
    ax.set_xlabel('Número Par (N)', fontsize=16, color='white')
    ax.set_ylabel('Número de Pares de Primos g(N)', fontsize=16, color='white')
    ax.grid(True, linestyle='--', alpha=0.2)
    ax.legend(loc='upper left', fontsize=12)
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
    if os.path.exists(plot_filename):
        os.remove(plot_filename)
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to {plot_filename}")

if __name__ == "__main__":
    main()
