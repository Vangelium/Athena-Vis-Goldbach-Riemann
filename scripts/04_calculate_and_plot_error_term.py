
import csv
import os
import math
import matplotlib.pyplot as plt

# Twin prime constant
C2 = 0.6601618158468695739278121100145557784326

def get_prime_factors(n, primes_list):
    """Finds the unique prime factors of a number n."""
    factors = set()
    d = n
    for prime in primes_list:
        if prime * prime > d:
            break
        if d % prime == 0:
            factors.add(prime)
            while d % prime == 0:
                d //= prime
    if d > 1:
        factors.add(d)
    return list(factors)

def sieve_of_eratosthenes(limit):
    """Generates primes up to a limit."""
    primes = [True] * (limit + 1)
    if limit >= 0: primes[0] = False
    if limit >= 1: primes[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if primes[i]:
            for multiple in range(i*i, limit + 1, i):
                primes[multiple] = False
    return [i for i, is_prime in enumerate(primes) if is_prime]

def calculate_hardy_littlewood(n, prime_factors):
    """Calculates the Hardy-Littlewood asymptotic approximation for g(N)."""
    if n <= 2 or n % 2 != 0:
        return 0
    main_term = (n / (math.log(n)**2))
    product_term = 1.0
    for p in prime_factors:
        if p != 2:
            product_term *= (p - 1) / (p - 2)
    return 2 * C2 * main_term * product_term

def main():
    """Main function to calculate and plot the error term Delta(N)."""
    data_filename = os.path.join(os.path.dirname(__file__), '..', 'data', 'goldbach_counts.csv')
    output_csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'goldbach_full_analysis.csv')
    plot_filename = os.path.join(os.path.dirname(__file__), '..', 'plots', '03_delta_n_vs_n.png')

    n_values, g_n_values = [], []
    print(f"Reading data from {data_filename}...")
    with open(data_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            n_values.append(int(row['N']))
            g_n_values.append(int(row['g(N)']))
    print("Data reading complete.")

    max_n = n_values[-1]
    print(f"Generating primes up to {int(max_n**0.5)} for factorization...")
    primes_for_factorization = sieve_of_eratosthenes(int(max_n**0.5) + 1)
    print("Prime generation complete.")

    print("Calculating error term Delta(N)...")
    delta_values = []
    full_analysis_data = []
    for i, n in enumerate(n_values):
        g_n_real = g_n_values[i]
        prime_factors = get_prime_factors(n, primes_for_factorization)
        asymptotic_approx = calculate_hardy_littlewood(n, prime_factors)
        delta_n = g_n_real - asymptotic_approx
        delta_values.append(delta_n)
        full_analysis_data.append({
            'N': n,
            'g(N)_real': g_n_real,
            'g(N)_asymptotic': asymptotic_approx,
            'Delta(N)': delta_n
        })
    print("Calculation complete.")

    print(f"Saving full analysis data to {output_csv_path}...")
    with open(output_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['N', 'g(N)_real', 'g(N)_asymptotic', 'Delta(N)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(full_analysis_data)
    print("Data saved.")

    print(f"Generating plot and saving to {plot_filename}...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(15, 10))

    ax.plot(n_values, delta_values, 'o', markersize=1, color='#FFD700', alpha=0.6) # Gold color
    ax.axhline(0, color='red', linestyle='--', linewidth=1, label='Cero')

    ax.set_title('Término de Error $\Delta(N) = g(N)_{real} - g(N)_{asintótico}$', fontsize=20, color='white')
    ax.set_xlabel('Número Par (N)', fontsize=16, color='white')
    ax.set_ylabel('Error $\Delta(N)$', fontsize=16, color='white')
    ax.grid(True, linestyle='--', alpha=0.2)
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to {plot_filename}")

if __name__ == "__main__":
    main()
