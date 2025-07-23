
import csv
import os
import matplotlib.pyplot as plt

def plot_g_n():
    """Reads Goldbach counts and plots g(N) vs. N."""
    data_filename = os.path.join(os.path.dirname(__file__), '..', 'data', 'goldbach_counts.csv')
    plot_filename = os.path.join(os.path.dirname(__file__), '..', 'plots', '01_g_n_vs_n_100k.png')

    n_values = []
    g_n_values = []

    print(f"Reading data from {data_filename}...")
    with open(data_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            n_values.append(int(row['N']))
            g_n_values.append(int(row['g(N)']))
    print("Data reading complete.")

    print(f"Generating plot and saving to {plot_filename}...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(15, 10))

    # Use smaller markers for a denser plot
    ax.plot(n_values, g_n_values, 'o', markersize=1, color='cyan', alpha=0.6)

    ax.set_title('Conteo de Pares de Goldbach g(N) vs. N (hasta 100,000)', fontsize=20, color='white')
    ax.set_xlabel('Número Par (N)', fontsize=16, color='white')
    ax.set_ylabel('Número de Pares de Primos g(N)', fontsize=16, color='white')
    ax.grid(True, linestyle='--', alpha=0.2)
    
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    # Ensure the plots directory exists
    os.makedirs(os.path.dirname(plot_filename), exist_ok=True)

    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to {plot_filename}")

if __name__ == "__main__":
    plot_g_n()
