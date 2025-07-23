import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

def load_delta_n(filepath):
    """Carga la columna Delta(N) del archivo CSV."""
    print(f"Cargando Delta(N) desde: {filepath}")
    df = pd.read_csv(filepath)
    if 'Delta(N)' not in df.columns:
        raise ValueError("La columna 'Delta(N)' no se encontró en el archivo CSV.")
    return df['Delta(N)'].values

def load_riemann_zeros(filepath, num_zeros=100):
    """Carga los ceros de Riemann desde el archivo de texto."""
    print(f"Cargando los primeros {num_zeros} ceros de Riemann desde: {filepath}")
    zeros = []
    try:
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                if i >= num_zeros: break
                try:
                    zeros.append(float(line.strip()))
                except ValueError:
                    print(f"Advertencia: No se pudo convertir la línea '{line.strip()}' a flotante.")
                    continue
    except FileNotFoundError:
        raise FileNotFoundError(f"El archivo de ceros de Riemann no se encontró en: {filepath}")
    return np.array(zeros)

def perform_fft_analysis(delta_n_series):
    """Realiza la FFT y calcula el espectro de potencia."""
    N = len(delta_n_series)
    yf = np.fft.fft(delta_n_series)
    xf = np.fft.fftfreq(N, 1)
    power_spectrum = 2.0/N * np.abs(yf[0:N//2])
    frequencies = xf[0:N//2]
    return frequencies, power_spectrum

def find_and_match_peaks(frequencies, power_spectrum, riemann_zeros, N_data, min_power_threshold=1e-4, freq_tolerance=5e-4):
    """
    Encuentra picos prominentes en el espectro de potencia y los compara con los ceros de Riemann.
    N_data es la longitud de la serie original Delta(N).
    """
    detected_peaks_freq = []
    for i in range(1, len(power_spectrum) - 1):
        if power_spectrum[i] > power_spectrum[i-1] and power_spectrum[i] > power_spectrum[i+1]:
            if power_spectrum[i] > min_power_threshold: # Filtrar por potencia mínima
                detected_peaks_freq.append(frequencies[i])

    matched_pairs = [] # (frecuencia_pico, frecuencia_cero_riemann)
    matched_riemann_zeros_freq = []
    
    # Escalar los ceros de Riemann a la misma unidad de frecuencia del eje X (ciclos por N)
    scaled_riemann_zeros_freq = [zero / (2 * np.pi * N_data) for zero in riemann_zeros]

    for peak_freq in detected_peaks_freq:
        for r_zero_freq in scaled_riemann_zeros_freq:
            if abs(peak_freq - r_zero_freq) < freq_tolerance:
                matched_pairs.append((peak_freq, r_zero_freq))
                matched_riemann_zeros_freq.append(r_zero_freq)
                break # Mover al siguiente pico detectado una vez que se encuentra una coincidencia

    return detected_peaks_freq, matched_pairs, matched_riemann_zeros_freq

def plot_spectrum(frequencies, power_spectrum, riemann_zeros, output_path, N_data, matched_riemann_zeros_freq):
    """Genera el gráfico del espectro de potencia con los ceros de Riemann y picos coincidentes."""
    plt.figure(figsize=(15, 8))
    plt.plot(frequencies, power_spectrum, label='Espectro de Potencia de Delta(N)', color='blue', alpha=0.7)
    plt.title('Espectro de Potencia de Delta(N) y Ceros de Riemann')
    plt.xlabel('Frecuencia (ciclos por N)')
    plt.ylabel('Potencia')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.yscale('log') # Escala logarítmica en el eje Y
    plt.xlim(0, 0.0001) # Ajustar el rango de frecuencia para ver los ceros de Riemann

    # Superponer los ceros de Riemann escalados
    scaled_riemann_zeros_freq = [zero / (2 * np.pi * N_data) for zero in riemann_zeros]
    for r_zero_freq in scaled_riemann_zeros_freq:
        plt.axvline(x=r_zero_freq, color='red', linestyle=':', alpha=0.6, label='Cero de Riemann')

    # Resaltar los ceros de Riemann que coinciden con picos
    for matched_freq in matched_riemann_zeros_freq:
        plt.axvline(x=matched_freq, color='green', linestyle='-', linewidth=4, alpha=1.0, label='Cero de Riemann Coincidente')

    # Eliminar etiquetas duplicadas de la leyenda
    handles, labels = plt.gca().get_legend_handles_labels()
    unique_labels = []
    unique_handles = []
    for i, label in enumerate(labels):
        if label not in unique_labels:
            unique_labels.append(label)
            unique_handles.append(handles[i])
    plt.legend(unique_handles, unique_labels)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.show()
    print(f"Gráfico del espectro guardado en: {output_path}")

# --- Ejecución Principal ---

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error: Proporciona la ruta al archivo CSV de Goldbach y al archivo de ceros de Riemann.")
        print("Uso: python riemann_goldbach_analysis.py <ruta_goldbach_csv> <ruta_ceros_riemann_txt>")
        sys.exit(1)
        
    goldbach_filepath = sys.argv[1]
    riemann_zeros_filepath = sys.argv[2]
    output_plot_path = r'C:\Users\Yonnahs\Athena-Vis-Goldbach-Riemann\plots\delta_n_spectrum_riemann_zeros.png'

    try:
        delta_n_series = load_delta_n(goldbach_filepath)
        N_data = len(delta_n_series) # Longitud de la serie Delta(N)
        riemann_zeros = load_riemann_zeros(riemann_zeros_filepath)
        
        frequencies, power_spectrum = perform_fft_analysis(delta_n_series)

        print("\n--- Estadísticas del Espectro de Potencia ---")
        print(f"Potencia Máxima: {np.max(power_spectrum):.6f}")
        print(f"Potencia Mínima: {np.min(power_spectrum):.6f}")
        print(f"Potencia Media: {np.mean(power_spectrum):.6f}")
        print(f"Percentil 99 de Potencia: {np.percentile(power_spectrum, 99):.6f}")
        print(f"Percentil 95 de Potencia: {np.percentile(power_spectrum, 95):.6f}")
        print(f"Percentil 90 de Potencia: {np.percentile(power_spectrum, 90):.6f}")

        detected_peaks_freq, matched_pairs, matched_riemann_zeros_freq = find_and_match_peaks(
            frequencies, power_spectrum, riemann_zeros, N_data,
            min_power_threshold=0.25, freq_tolerance=1e-3 # Umbrales ajustados
        )
        
        plot_spectrum(frequencies, power_spectrum, riemann_zeros, output_plot_path, N_data, matched_riemann_zeros_freq)
        
        print("\n--- Resumen del Análisis Cuantitativo ---")
        print(f"Número total de picos detectados: {len(detected_peaks_freq)}")
        print(f"Número de ceros de Riemann analizados: {len(riemann_zeros)}")
        print(f"Número de coincidencias encontradas: {len(matched_pairs)}")
        
        if len(matched_pairs) > 0:
            avg_diff = np.mean([abs(p - r) for p, r in matched_pairs])
            print(f"Diferencia promedio entre picos y ceros coincidentes: {avg_diff:.6f}")
        else:
            print("No se encontraron coincidencias para calcular la diferencia promedio.")
        
    except Exception as e:
        print(f"Ocurrió un error durante el análisis: {e}")
        sys.exit(1)