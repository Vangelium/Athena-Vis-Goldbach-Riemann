
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import math

# The imaginary parts (ordinates) of the first few non-trivial Riemann Zeta zeros
RIEMANN_ZEROS_GAMMAS = [
    14.1347251417, 21.0220396388, 25.0108575801, 30.4248761259,
    32.9350615877, 37.5861781588, 40.9187190121, 43.3270732809,
    48.0051508811, 49.7738324777, 52.9703214777, 56.446247697,
    59.347044003, 60.831778525, 65.085804636, 67.079810529,
    69.546401711, 72.067157674, 75.704690699, 77.144840069
]

def main():
    """Performs the corrected frequency analysis and compares to Riemann zeros."""
    analysis_filename = os.path.join(os.path.dirname(__file__), '..', 'data', 'goldbach_full_analysis.csv')
    plot_filename = os.path.join(os.path.dirname(__file__), '..', 'plots', '06_corrected_spectrum_vs_riemann.png')

    n_values, delta_values = [], []
    print(f"Reading data from {analysis_filename}...")
    with open(analysis_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            n_values.append(int(row['N']))
            delta_values.append(float(row['Delta(N)']))
    print("Data reading complete.")

    # --- Step 1: Resample the signal to be uniform in log(N) space ---
    print("Resampling data to be uniform in log(N) space...")
    log_n_values = np.log(n_values)
    delta_values = np.array(delta_values)

    # Create a new, evenly spaced grid in log space
    num_samples = len(n_values) * 2 # Increase sampling for better resolution
    log_n_grid = np.linspace(log_n_values.min(), log_n_values.max(), num_samples)

    # Interpolate the delta values onto the new grid
    interpolated_delta = np.interp(log_n_grid, log_n_values, delta_values)
    print("Resampling complete.")

    # --- Step 2: Perform FFT on the correctly sampled signal ---
    print("Performing Fourier Transform on resampled data...")
    # The sampling interval is the distance between points on our new grid
    sampling_interval = log_n_grid[1] - log_n_grid[0]
    
    # Perform FFT
    fft_result = np.fft.fft(interpolated_delta)
    power_spectrum = np.abs(fft_result)**2

    # The frequency axis for the log-spaced data
    freqs = np.fft.fftfreq(num_samples, d=sampling_interval)
    
    # We only need the positive frequencies
    positive_freqs = freqs[:num_samples // 2]
    positive_power = power_spectrum[:num_samples // 2]
    print("FFT complete.")

    # --- Step 3: Generate the final, correct plot ---
    print(f"Generating final comparison plot and saving to {plot_filename}...")
    
    # The theoretical frequencies from Riemann zeros are gamma / (2*pi)
    riemann_freqs = [gamma / (2 * math.pi) for gamma in RIEMANN_ZEROS_GAMMAS]

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(15, 10))

    # Plot the new, correct spectrum
    ax.plot(positive_freqs, positive_power, color='#FFD700', linewidth=1.5, label='Espectro de $\Delta(\log N)$')
    ax.set_yscale('log')

    # Plot vertical lines for the Riemann zero frequencies
    for i, r_freq in enumerate(riemann_freqs):
        color = '#00FF00' if i == 0 else 'cyan' # Highlight first zero
        linewidth = 2.5 if i == 0 else 1.0
        label = f'Cero de Riemann {i+1} ({r_freq:.2f})' if i < 4 else None # Label first few
        ax.axvline(x=r_freq, color=color, linestyle='--', linewidth=linewidth, alpha=0.9, label=label)

    ax.set_title('Análisis Espectral Corregido vs. Ceros de Riemann', fontsize=20, color='white')
    ax.set_xlabel('Frecuencia (γ / 2π)', fontsize=16, color='white')
    ax.set_ylabel('Potencia Espectral (log)', fontsize=16, color='white')
    ax.grid(True, linestyle='--', alpha=0.2)
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.legend()

    # Zoom in on the range where the first few zeros appear
    ax.set_xlim(0, 10) # The first few zeros have frequencies in this range
    ax.set_ylim(bottom=1e9) # Adjust ylim to cut out low-level noise and focus on peaks

    os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
    # Delete old file if it exists to prevent caching issues
    if os.path.exists(plot_filename):
        os.remove(plot_filename)
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to {plot_filename}")

if __name__ == "__main__":
    main()
