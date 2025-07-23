
import csv
import os
import numpy as np
import matplotlib.pyplot as plt

def moving_average(data, window_size):
    """Calculates the moving average of a list of data."""
    if window_size <= 0:
        raise ValueError("Window size must be positive.")
    if window_size > len(data):
        # If window is larger than data, return a constant array of the mean
        return np.full_like(data, np.mean(data))

    # Pad the data to handle edges and ensure output length is same as input
    padded_data = np.pad(data, (window_size // 2, window_size - 1 - window_size // 2), mode='edge')
    return np.convolve(padded_data, np.ones(window_size)/window_size, mode='valid')

def get_divisibility_category(n):
    """Categorizes N based on its divisibility by small primes."""
    if n % 3 == 0:
        return 'Divisible por 3'
    elif n % 5 == 0:
        return 'Divisible por 5 (no por 3)'
    elif n % 7 == 0:
        return 'Divisible por 7 (no por 3 ni 5)'
    else:
        return 'Otros'

def main():
    """Calculates and plots the refined Goldbach model with explicit divisibility modeling."""
    analysis_filename = os.path.join(os.path.dirname(__file__), '..', 'data', 'goldbach_full_analysis.csv')
    plot_filename = os.path.join(os.path.dirname(__file__), '..', 'plots', '10_g_n_refined_model_divisibility.png')

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

    # --- Group Delta(N) by divisibility and smooth each group ---
    window_size = 500 # Same window size as before
    
    # Prepare data structures for each category
    categorized_data = {
        'Divisible por 3': {'N': [], 'Delta': []},
        'Divisible por 5 (no por 3)': {'N': [], 'Delta': []},
        'Divisible por 7 (no por 3 ni 5)': {'N': [], 'Delta': []},
        'Otros': {'N': [], 'Delta': []}
    }

    # Populate categorized_data
    for i, n in enumerate(n_values):
        category = get_divisibility_category(n)
        categorized_data[category]['N'].append(n)
        categorized_data[category]['Delta'].append(delta_values[i])

    # Smooth Delta(N) for each category and store interpolated functions
    smoothed_delta_interpolators = {}
    for category, data in categorized_data.items():
        if len(data['N']) > 1: # Need at least 2 points for interpolation
            # Sort by N before smoothing to ensure correct order
            sorted_indices = np.argsort(data['N'])
            sorted_n = np.array(data['N'])[sorted_indices]
            sorted_delta = np.array(data['Delta'])[sorted_indices]
            
            smoothed_delta = moving_average(sorted_delta, window_size)
            
            # Create an interpolator function for this category's smoothed delta
            smoothed_delta_interpolators[category] = lambda x, sn=sorted_n, sd=smoothed_delta: np.interp(x, sn, sd)
        elif len(data['N']) == 1:
            # If only one point, the smoothed value is just that point
            smoothed_delta_interpolators[category] = lambda x, sd=data['Delta'][0]: sd
        else:
            # If no data for category, return 0
            smoothed_delta_interpolators[category] = lambda x: 0.0

    # --- Calculate Refined Model with explicit divisibility ---
    print("Calculating refined model with explicit divisibility...")
    g_n_refined_values_div = np.zeros_like(g_n_real_values, dtype=float)
    
    for i, n in enumerate(n_values):
        category = get_divisibility_category(n)
        # Get the smoothed delta for this specific N from its category's interpolator
        interpolated_smoothed_delta = smoothed_delta_interpolators[category](n)
        g_n_refined_values_div[i] = g_n_asymptotic_values[i] + interpolated_smoothed_delta
    print("Refined model calculation complete.")

    # --- Plotting ---
    print(f"Generating plot and saving to {plot_filename}...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(15, 10))

    # Plot real data
    ax.plot(n_values, g_n_real_values, 'o', markersize=1, color='cyan', alpha=0.6, label='Datos Reales g(N)')
    
    # Plot asymptotic approximation
    ax.plot(n_values, g_n_asymptotic_values, '-', color='magenta', linewidth=2, label='Aproximación Asintótica (Hardy-Littlewood)')

    # Plot refined model with divisibility
    ax.plot(n_values, g_n_refined_values_div, '-', color='lime', linewidth=2, label='Modelo Refinado (Divisibilidad Explícita)')

    ax.set_title('g(N) Real vs. Aproximación Asintótica vs. Modelo Refinado (Divisibilidad)', fontsize=20, color='white')
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
