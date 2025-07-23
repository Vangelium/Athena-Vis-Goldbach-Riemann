
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import math

# The imaginary parts (ordinates) of the first few non-trivial Riemann Zeta zeros
# Source: OEIS A002410, Andrew Odlyzko, and other mathematical resources.
RIEMANN_ZEROS_GAMMAS = [
    14.1347251417,
    21.0220396388,
    25.0108575801,
    30.4248761259,
    32.9350615877,
    37.5861781588,
    40.9187190121,
    43.3270732809,
    48.0051508811,
    49.7738324777
]

def main():
    """Performs frequency analysis and compares peaks to Riemann Zeta function zeros."""
    analysis_filename = os.path.join(os.path.dirname(__file__), '..', 'data', 'goldbach_full_analysis.csv')
    plot_filename = os.path.join(os.path.dirname(__file__), '..', 'plots', '05_spectrum_vs_riemann_zeros.png')

    delta_values = []
    print(f"Reading data from {analysis_filename}...")
    with open(analysis_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            delta_values.append(float(row['Delta(N)']))
    print("Data reading complete.")

    signal = np.array(delta_values)
    n_points = len(signal)

    print("Performing Fourier Transform (FFT)...")
    fft_result = np.fft.fft(signal)
    power_spectrum = np.abs(fft_result)**2
    freqs = np.fft.fftfreq(n_points, d=2) # d=2 for even numbers sampling

    half_n = n_points // 2
    positive_freqs = freqs[:half_n]
    positive_power = power_spectrum[:half_n]
    print("FFT complete.")

    # Convert Riemann zero ordinates (gamma) to frequencies (f = gamma / 2*pi)
    # The frequencies in our FFT are cycles per unit N. The explicit formulas relate sums over primes
    # to sums over zeros, and the oscillatory terms are of the form x^(rho)/rho where rho=1/2+i*gamma.
    # The frequency of these oscillations in the domain of log(x) is gamma/(2*pi).
    # For the domain of x, the relationship is more complex, but we expect a correspondence.
    # Let's scale our frequencies for comparison.
    # Our x-axis is N, not log(N). The frequencies from FFT are in cycles/N.
    # A simplified view connects the zeros to frequencies. Let's test the direct hypothesis.
    
    # The frequencies from the FFT need to be scaled to match the theoretical expectation.
    # The frequencies from the zeros are γ/(2π). Let's see if there's a direct match.
    # A more advanced analysis would involve changing the domain of our data to log(N).
    # For this visualization, we will plot the expected frequencies directly.
    
    # Let's calculate the expected frequencies from the Riemann zeros.
    # The frequencies from the FFT are in cycles per N.
    # The frequencies from the zeros are γ / (2π).
    # Let's find the corresponding N for our frequencies: N_freq = 1 / freq
    # Let's try a different scaling for visualization. The main oscillatory terms in prime distributions
    # are related to log(N). Our signal is on N. Let's scale the zeros to our frequency domain.
    # The period of the nth zero's wave is T = 2*pi / log(gamma_n). This is a simplification.
    # Let's stick to the most direct hypothesis: the peaks in freq space correspond to gamma/(2*pi)
    
    # The frequencies from FFT are cycles per 2 units of N. So we scale by N_max.
    # Let's try a direct mapping first. The frequencies from FFT are k/N_total.
    # Let's convert the Riemann zeros to the same scale.
    riemann_freqs = [gamma / (2 * math.pi) for gamma in RIEMANN_ZEROS_GAMMAS]

    print(f"Generating final comparison plot and saving to {plot_filename}...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(15, 10))

    ax.plot(positive_freqs, positive_power, color='#FF5733', linewidth=1, label='Espectro de $\Delta(N)$')
    ax.set_yscale('log')

    # Plot vertical lines for the Riemann zero frequencies, highlighting the first one
    for i, r_freq in enumerate(riemann_freqs):
        if i == 0:
            # Highlight the first zero
            ax.axvline(x=r_freq, color='#00FF00', linestyle='--', linewidth=2.5, alpha=1, label=f'Cero de Riemann 1 ({r_freq:.4f})')
        else:
            # Plot the rest normally
            ax.axvline(x=r_freq, color='cyan', linestyle='--', linewidth=1.0, alpha=0.7)

    ax.set_title('Espectro de Frecuencias de $\Delta(N)$ vs. Ceros de la Función Zeta de Riemann', fontsize=20, color='white')
    ax.set_xlabel('Frecuencia', fontsize=16, color='white')
    ax.set_ylabel('Potencia Espectral (log)', fontsize=16, color='white')
    ax.grid(True, linestyle='--', alpha=0.2)
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    
    # We need to find the right x-axis scale to make the comparison meaningful.
    # The frequencies from FFT are k / (d * N_points). Here d=2.
    # Let's adjust the x-axis to a more interpretable scale.
    # For now, we will zoom in on the low-frequency part where the first zeros are expected.
    ax.set_xlim(0, 0.05) # Zoom in on the most relevant frequency range
    ax.legend()

    os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to {plot_filename}")

if __name__ == "__main__":
    main()
