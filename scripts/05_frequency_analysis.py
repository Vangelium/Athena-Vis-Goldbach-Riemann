
import csv
import os
import numpy as np
import matplotlib.pyplot as plt

def main():
    """Main function to perform frequency analysis on the Delta(N) error term."""
    analysis_filename = os.path.join(os.path.dirname(__file__), '..', 'data', 'goldbach_full_analysis.csv')
    plot_filename = os.path.join(os.path.dirname(__file__), '..', 'plots', '04_delta_n_frequency_spectrum.png')

    delta_values = []
    print(f"Reading data from {analysis_filename}...")
    with open(analysis_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            delta_values.append(float(row['Delta(N)']))
    print("Data reading complete.")

    # The signal is our Delta(N) term
    signal = np.array(delta_values)
    n_points = len(signal)

    print("Performing Fourier Transform (FFT)...")
    # Perform FFT
    fft_result = np.fft.fft(signal)
    # Calculate the power spectrum (amplitude squared)
    power_spectrum = np.abs(fft_result)**2

    # Generate the frequency axis. The sampling rate is 1 (one data point per even number).
    # We are interested in the frequencies, not the raw indices.
    # The frequencies range from 0 to 1/2 of the sampling rate.
    freqs = np.fft.fftfreq(n_points, d=2) # d=2 because we sample every 2 integers (even numbers)

    # We only need to plot the first half of the frequencies (positive frequencies)
    half_n = n_points // 2
    positive_freqs = freqs[:half_n]
    positive_power = power_spectrum[:half_n]
    print("FFT complete.")

    print(f"Generating plot and saving to {plot_filename}...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(15, 10))

    # We plot against frequency. Let's use a log scale for the y-axis to see peaks better.
    ax.plot(positive_freqs, positive_power, color='#FF5733', linewidth=1)
    ax.set_yscale('log')

    ax.set_title('Espectro de Frecuencias del Término de Error $\Delta(N)$', fontsize=20, color='white')
    ax.set_xlabel('Frecuencia (ciclos / unidad de N)', fontsize=16, color='white')
    ax.set_ylabel('Potencia (Amplitud Espectral al Cuadrado)', fontsize=16, color='white')
    ax.grid(True, linestyle='--', alpha=0.2)
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    # Optional: Zoom into a specific frequency range if needed, e.g., the lower frequencies
    # ax.set_xlim(0, 0.05)

    os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to {plot_filename}")

if __name__ == "__main__":
    main()
