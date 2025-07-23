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

def calculate_metrics(y_true, y_pred, model_name):
    """Calculates and prints MSE, MAE, and R^2 for a given model."""
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    mse = np.mean((y_true - y_pred)**2)
    mae = np.mean(np.abs(y_true - y_pred))
    
    ss_total = np.sum((y_true - np.mean(y_true))**2)
    ss_residual = np.sum((y_true - y_pred)**2)
    r_squared = 1 - (ss_residual / ss_total)

    print(f"\n--- Métricas para {model_name} ---")
    print(f"MSE (Error Cuadrático Medio): {mse:.4f}")
    print(f"MAE (Error Absoluto Medio): {mae:.4f}")
    print(f"R^2 (Coeficiente de Determinación): {r_squared:.4f}")
    return y_true - y_pred # Return errors for histogram

def main():
    """Main function to quantify model accuracy and plot error distributions."""
    analysis_filename = os.path.join(os.path.dirname(__file__), '..', 'data', 'goldbach_full_analysis.csv')
    plot_filename = os.path.join(os.path.dirname(__file__), '..', 'plots', '11_error_distribution_histograms_divisibility.png') # New filename

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

    # Calculate metrics for Asymptotic Model (remains the same)
    errors_asymptotic = calculate_metrics(g_n_real_values, g_n_asymptotic_values, "Aproximación Asintótica")

    # --- Re-calculate refined model with explicit divisibility (from 11_refined_goldbach_model_divisibility.py) ---
    window_size = 500 # Must be the same as in 11_refined_goldbach_model_divisibility.py

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

    # Calculate Refined Model with explicit divisibility
    print("Calculating refined model with explicit divisibility for metrics...")
    g_n_refined_values_div = np.zeros_like(g_n_real_values, dtype=float)
    
    for i, n in enumerate(n_values):
        category = get_divisibility_category(n)
        # Get the smoothed delta for this specific N from its category's interpolator
        interpolated_smoothed_delta = smoothed_delta_interpolators[category](n)
        g_n_refined_values_div[i] = g_n_asymptotic_values[i] + interpolated_smoothed_delta
    print("Refined model calculation complete.")

    # Calculate metrics for Refined Model (Divisibility Explicit)
    errors_refined_div = calculate_metrics(g_n_real_values, g_n_refined_values_div, "Modelo Refinado (Divisibilidad Explícita)")

    # --- Plotting Histograms ---
    print(f"Generating error distribution histograms and saving to {plot_filename}...")
    plt.style.use('dark_background')
    fig, axes = plt.subplots(1, 2, figsize=(18, 7), sharey=True)

    # Histogram for Asymptotic Model Errors
    axes[0].hist(errors_asymptotic, bins=50, color='magenta', alpha=0.7, edgecolor='white')
    axes[0].set_title('Distribución de Errores: Aproximación Asintótica', fontsize=16, color='white')
    axes[0].set_xlabel('Error (g(N) real - g(N) predicho)', fontsize=12, color='white')
    axes[0].set_ylabel('Frecuencia', fontsize=12, color='white')
    axes[0].tick_params(axis='x', colors='white')
    axes[0].tick_params(axis='y', colors='white')
    axes[0].grid(True, linestyle='--', alpha=0.2)

    # Histogram for Refined Model (Divisibility Explicit) Errors
    axes[1].hist(errors_refined_div, bins=50, color='lime', alpha=0.7, edgecolor='white')
    axes[1].set_title('Distribución de Errores: Modelo Refinado (Divisibilidad Explícita)', fontsize=16, color='white')
    axes[1].set_xlabel('Error (g(N) real - g(N) predicho)', fontsize=12, color='white')
    axes[1].tick_params(axis='x', colors='white')
    axes[1].tick_params(axis='y', colors='white')
    axes[1].grid(True, linestyle='--', alpha=0.2)

    plt.suptitle('Comparación de la Distribución de Errores del Modelo', fontsize=20, color='white')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
    if os.path.exists(plot_filename):
        os.remove(plot_filename)
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to {plot_filename}")

if __name__ == "__main__":
    main()