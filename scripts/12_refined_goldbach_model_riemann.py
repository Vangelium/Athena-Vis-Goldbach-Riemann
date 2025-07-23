import csv
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def moving_average(data, window_size):
    """Calculates the moving average of a list of data."""
    if window_size <= 0:
        raise ValueError("Window size must be positive.")
    if window_size > len(data):
        return np.full_like(data, np.mean(data))

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

def load_riemann_zeros(filepath, num_zeros=50):
    """Loads a specified number of Riemann zeros from a file."""
    zeros = []
    try:
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                if i >= num_zeros:
                    break
                try:
                    zeros.append(float(line.strip()))
                except ValueError:
                    print(f"Warning: Could not parse line as float: {line.strip()}")
        print(f"Loaded {len(zeros)} Riemann zeros from {filepath}")
    except FileNotFoundError:
        print(f"Error: Riemann zeros file not found at {filepath}")
    return np.array(zeros)

def main():
    """Calculates and plots the refined Goldbach model with Riemann zeros."""
    analysis_filename = os.path.join(os.path.dirname(__file__), '..', 'data', 'goldbach_full_analysis.csv')
    riemann_zeros_filename = os.path.join(os.path.dirname(__file__), '..', 'data', 'zeros_riemann.txt')
    plot_model_filename = os.path.join(os.path.dirname(__file__), '..', 'plots', '11_g_n_refined_model_riemann.png')
    plot_residual_spectrum_filename = os.path.join(os.path.dirname(__file__), '..', 'plots', '12_residual_spectrum_riemann.png')

    max_n_limit = 1_000_000 # User specified limit for plotting and metrics

    n_values, g_n_real_values, g_n_asymptotic_values, delta_values = [], [], [], []
    print(f"Reading data from {analysis_filename} up to N={max_n_limit}...")
    with open(analysis_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            n = int(row['N'])
            if n > max_n_limit:
                break
            n_values.append(n)
            g_n_real_values.append(float(row['g(N)_real']))
            g_n_asymptotic_values.append(float(row['g(N)_asymptotic']))
            delta_values.append(float(row['Delta(N)']))
    print("Data reading complete.")

    n_values = np.array(n_values)
    g_n_real_values = np.array(g_n_real_values)
    g_n_asymptotic_values = np.array(g_n_asymptotic_values)
    delta_values = np.array(delta_values)

    # --- Load Riemann Zeros ---
    num_riemann_zeros_to_use = 100 # Starting with 100, can be adjusted
    riemann_zeros = load_riemann_zeros(riemann_zeros_filename, num_riemann_zeros_to_use)
    if len(riemann_zeros) == 0:
        print("No Riemann zeros loaded. Exiting.")
        return

    # --- Group Delta(N) by divisibility and smooth each group (as in script 11) ---
    window_size = 500
    categorized_data = {
        'Divisible por 3': {'N': [], 'Delta': []},
        'Divisible por 5 (no por 3)': {'N': [], 'Delta': []},
        'Divisible por 7 (no por 3 ni 5)': {'N': [], 'Delta': []},
        'Otros': {'N': [], 'Delta': []}
    }

    for i, n in enumerate(n_values):
        category = get_divisibility_category(n)
        categorized_data[category]['N'].append(n)
        categorized_data[category]['Delta'].append(delta_values[i])

    smoothed_delta_interpolators = {}
    for category, data in categorized_data.items():
        if len(data['N']) > 1:
            sorted_indices = np.argsort(data['N'])
            sorted_n = np.array(data['N'])[sorted_indices]
            sorted_delta = np.array(data['Delta'])[sorted_indices]
            smoothed_delta = moving_average(sorted_delta, window_size)
            smoothed_delta_interpolators[category] = lambda x, sn=sorted_n, sd=smoothed_delta: np.interp(x, sn, sd)
        elif len(data['N']) == 1:
            smoothed_delta_interpolators[category] = lambda x, sd=data['Delta'][0]: sd
        else:
            smoothed_delta_interpolators[category] = lambda x: 0.0

    # --- Calculate Refined Model with explicit divisibility (without Riemann zeros initially) ---
    print("Calculating refined model with explicit divisibility...")
    g_n_refined_values_div = np.zeros_like(g_n_real_values, dtype=float)

    for i, n in enumerate(n_values):
        category = get_divisibility_category(n)
        interpolated_smoothed_delta = smoothed_delta_interpolators[category](n)
        g_n_refined_values_div[i] = g_n_asymptotic_values[i] + interpolated_smoothed_delta
    print("Refined model (divisibility only) calculation complete.")

    # --- Calculate Residual from Divisibility Model ---
    residual_divisibility = g_n_real_values - g_n_refined_values_div

    # --- Fit Riemann Oscillatory Terms to the Residual ---
    print(f"Fitting {len(riemann_zeros)} Riemann oscillatory terms to the residual...")
    # Construct the design matrix for linear regression
    # Each zero t contributes a cos(t*log(N)) and a sin(t*log(N)) term
    log_n_values = np.log(n_values)
    X = np.zeros((len(n_values), 2 * len(riemann_zeros)))
    for i, t in enumerate(riemann_zeros):
        X[:, 2*i] = np.cos(t * log_n_values)
        X[:, 2*i + 1] = np.sin(t * log_n_values)

    # Solve for the coefficients using least squares
    # rcond=None to suppress FutureWarning
    coefficients, residuals_sum_sq, rank, s = np.linalg.lstsq(X, residual_divisibility, rcond=None)

    # Calculate the Riemann correction term based on the fitted coefficients
    riemann_correction_term = np.dot(X, coefficients)
    print("Riemann oscillatory terms fitting complete.")

    # --- Calculate Final Refined Model with Divisibility and Fitted Riemann zeros ---
    print("Calculating final refined model...")
    g_n_refined_values_riemann = g_n_refined_values_div + riemann_correction_term
    print("Final refined model calculation complete.")

    # --- Calculate Residual of the Final Model ---
    residual = g_n_real_values - g_n_refined_values_riemann

    # --- Calculate and Analyze Metrics of Error ---
    mse = mean_squared_error(g_n_real_values, g_n_refined_values_riemann)
    mae = mean_absolute_error(g_n_real_values, g_n_refined_values_riemann)
    r2 = r2_score(g_n_real_values, g_n_refined_values_riemann)

    print(f"Metrics for N up to {max_n_limit} (Divisibility + Fitted Riemann Model):")
    print(f"  MSE: {mse:.6f}")
    print(f"  MAE: {mae:.6f}")
    print(f"  R^2: {r2:.6f}")

    # --- Plotting g(N) Real vs. Modelo Refinado (Divisibilidad + Fitted Riemann) ---
    plot_model_filename = os.path.join(os.path.dirname(__file__), '..', 'plots', '11_g_n_refined_model_riemann.png')
    print(f"Generating g(N) plot and saving to {plot_model_filename}...")
    plt.style.use('dark_background')
    fig1, ax1 = plt.subplots(figsize=(15, 10))

    ax1.plot(n_values, g_n_real_values, 'o', markersize=1, color='cyan', alpha=0.6, label='Datos Reales g(N)')
    ax1.plot(n_values, g_n_asymptotic_values, '-', color='magenta', linewidth=2, label='Aproximación Asintótica (Hardy-Littlewood)')
    ax1.plot(n_values, g_n_refined_values_riemann, '-', color='lime', linewidth=2, label='Modelo Refinado (Divisibilidad + Riemann)')

    ax1.set_title(f'g(N) Real vs. Modelo Refinado (Divisibilidad + Riemann) hasta N={max_n_limit}', fontsize=20, color='white')
    ax1.set_xlabel('Número Par (N)', fontsize=16, color='white')
    ax1.set_ylabel('Número de Pares de Primos g(N)', fontsize=16, color='white')
    ax1.grid(True, linestyle='--', alpha=0.2)
    ax1.legend(loc='upper left', fontsize=12)
    ax1.tick_params(axis='x', colors='white')
    ax1.tick_params(axis='y', colors='white')

    os.makedirs(os.path.dirname(plot_model_filename), exist_ok=True)
    if os.path.exists(plot_model_filename):
        os.remove(plot_model_filename)
    plt.savefig(plot_model_filename, dpi=300, bbox_inches='tight')
    print(f"g(N) plot saved successfully to {plot_model_filename}")

    # --- Plotting Espectro de Frecuencias del Residuo Final ---
    plot_residual_spectrum_filename = os.path.join(os.path.dirname(__file__), '..', 'plots', '12_residual_spectrum_riemann.png')
    print(f"Generating residual spectrum plot and saving to {plot_residual_spectrum_filename}...")
    fig2, ax2 = plt.subplots(figsize=(15, 10))

    N_samples = len(residual)
    yf = fft(residual)
    xf = fftfreq(N_samples, 1) # Assuming N values are spaced by 1 (even numbers)

    # We are interested in positive frequencies and magnitude
    ax2.plot(xf[1:N_samples//2], 2.0/N_samples * np.abs(yf[1:N_samples//2]), color='yellow')
    ax2.set_title(f'Espectro de Frecuencias del Residuo Final (hasta N={max_n_limit})', fontsize=20, color='white')
    ax2.set_xlabel('Frecuencia', fontsize=16, color='white')
    ax2.set_ylabel('Amplitud Normalizada', fontsize=16, color='white')
    ax2.grid(True, linestyle='--', alpha=0.2)
    ax2.tick_params(axis='x', colors='white')
    ax2.tick_params(axis='y', colors='white')
    ax2.set_xlim(0, 0.05) # Focus on lower frequencies, adjust as needed

    os.makedirs(os.path.dirname(plot_residual_spectrum_filename), exist_ok=True)
    if os.path.exists(plot_residual_spectrum_filename):
        os.remove(plot_residual_spectrum_filename)
    plt.savefig(plot_residual_spectrum_filename, dpi=300, bbox_inches='tight')
    print(f"Residual spectrum plot saved successfully to {plot_residual_spectrum_filename}")

    # --- Plotting Espectro de Frecuencias de Delta(N) ---
    plot_delta_spectrum_filename = os.path.join(os.path.dirname(__file__), '..', 'plots', '13_delta_n_spectrum.png')
    print(f"Generating Delta(N) spectrum plot and saving to {plot_delta_spectrum_filename}...")
    fig3, ax3 = plt.subplots(figsize=(15, 10))

    N_samples_delta = len(delta_values)
    yf_delta = fft(delta_values)
    xf_delta = fftfreq(N_samples_delta, 1) # Assuming N values are spaced by 1 (even numbers)

    ax3.plot(xf_delta[1:N_samples_delta//2], 2.0/N_samples_delta * np.abs(yf_delta[1:N_samples_delta//2]), color='orange')
    ax3.set_title(f'Espectro de Frecuencias de Delta(N) (hasta N={max_n_limit})', fontsize=20, color='white')
    ax3.set_xlabel('Frecuencia', fontsize=16, color='white')
    ax3.set_ylabel('Amplitud Normalizada', fontsize=16, color='white')
    ax3.grid(True, linestyle='--', alpha=0.2)
    ax3.tick_params(axis='x', colors='white')
    ax3.tick_params(axis='y', colors='white')
    ax3.set_xlim(0, 0.05) # Focus on lower frequencies, adjust as needed

    os.makedirs(os.path.dirname(plot_delta_spectrum_filename), exist_ok=True)
    if os.path.exists(plot_delta_spectrum_filename):
        os.remove(plot_delta_spectrum_filename)
    plt.savefig(plot_delta_spectrum_filename, dpi=300, bbox_inches='tight')
    print(f"Delta(N) spectrum plot saved successfully to {plot_delta_spectrum_filename}")

if __name__ == "__main__":
    main()