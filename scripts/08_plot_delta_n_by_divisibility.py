
import csv
import os
import matplotlib.pyplot as plt

def main():
    """Plots Delta(N) vs. N, colored by divisibility properties of N."""
    analysis_filename = os.path.join(os.path.dirname(__file__), '..', 'data', 'goldbach_full_analysis.csv')
    plot_filename = os.path.join(os.path.dirname(__file__), '..', 'plots', '07_delta_n_by_divisibility.png')

    # Data structures to hold points for each category
    data_by_category = {
        'Divisible por 3': {'N': [], 'Delta': []},
        'Divisible por 5 (no por 3)': {'N': [], 'Delta': []},
        'Divisible por 7 (no por 3 ni 5)': {'N': [], 'Delta': []},
        'Otros': {'N': [], 'Delta': []}
    }

    print(f"Reading data from {analysis_filename} and categorizing...")
    with open(analysis_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            n = int(row['N'])
            delta_n = float(row['Delta(N)'])

            if n % 3 == 0:
                data_by_category['Divisible por 3']['N'].append(n)
                data_by_category['Divisible por 3']['Delta'].append(delta_n)
            elif n % 5 == 0:
                data_by_category['Divisible por 5 (no por 3)']['N'].append(n)
                data_by_category['Divisible por 5 (no por 3)']['Delta'].append(delta_n)
            elif n % 7 == 0:
                data_by_category['Divisible por 7 (no por 3 ni 5)']['N'].append(n)
                data_by_category['Divisible por 7 (no por 3 ni 5)']['Delta'].append(delta_n)
            else:
                data_by_category['Otros']['N'].append(n)
                data_by_category['Otros']['Delta'].append(delta_n)
    print("Data categorization complete.")

    print(f"Generating plot and saving to {plot_filename}...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(15, 10))

    # Define colors for each category
    colors = {
        'Divisible por 3': '#FF00FF',  # Magenta
        'Divisible por 5 (no por 3)': '#00FFFF', # Cyan
        'Divisible por 7 (no por 3 ni 5)': '#FFFF00', # Yellow
        'Otros': '#808080' # Gray
    }

    # Plot each category
    # Plot 'Otros' first so other categories are on top
    ax.plot(data_by_category['Otros']['N'], data_by_category['Otros']['Delta'],
            'o', markersize=1, color=colors['Otros'], alpha=0.3, label='Otros')

    for category, data in data_by_category.items():
        if category != 'Otros': # Plot others on top
            ax.plot(data['N'], data['Delta'],
                    'o', markersize=1.5, color=colors[category], alpha=0.7, label=category)

    ax.axhline(0, color='red', linestyle='--', linewidth=1, label='Cero')

    ax.set_title('Término de Error $\Delta(N)$ Coloreado por Divisibilidad', fontsize=20, color='white')
    ax.set_xlabel('Número Par (N)', fontsize=16, color='white')
    ax.set_ylabel('Error $\Delta(N)$', fontsize=16, color='white')
    ax.grid(True, linestyle='--', alpha=0.2)
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.legend(loc='lower left', fontsize=12)

    os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
    # Delete old file if it exists to prevent caching issues
    if os.path.exists(plot_filename):
        os.remove(plot_filename)
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to {plot_filename}")

if __name__ == "__main__":
    main()
