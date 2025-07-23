
import csv
import os
import math
import matplotlib.pyplot as plt

# Twin prime constant
C2 = 0.6601618158468695739278121100145557784326

def get_prime_factors(n, primes_list):
    """Finds the unique prime factors of a number n from a pre-computed list of primes."""
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
    """Generates primes up to a limit for factorization purposes."""
    primes = [True] * (limit + 1)
    if limit >= 0: primes[0] = False
    if limit >= 1: primes[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if primes[i]:
            for multiple in range(i*i, limit + 1, i):
                primes[multiple] = False
    prime_numbers = [i for i, is_prime in enumerate(primes) if is_prime]
    return prime_numbers

def calculate_hardy_littlewood(n, prime_factors):
    """Calculates the Hardy-Littlewood asymptotic approximation for g(N)."""
    if n <= 2 or n % 2 != 0:
        return 0
    
    # Main term from Prime Number Theorem
    main_term = (n / (math.log(n)**2))
    
    # Product term for odd prime factors
    product_term = 1.0
    for p in prime_factors:
        if p != 2: # Only for odd primes
            product_term *= (p - 1) / (p - 2)
            
    return 2 * C2 * main_term * product_term

def main():
    """Main function to read data, calculate approximation, and plot."""
    data_filename = os.path.join(os.path.dirname(__file__), '..', 'data', 'goldbach_counts.csv')
    plot_filename = os.path.join(os.path.dirname(__file__), '..', 'plots', '02_g_n_and_asymptotic.png')

    n_values = []
    g_n_values = []

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

    print("Calculating Hardy-Littlewood approximation...")
    asymptotic_values = []
    for n in n_values:
        prime_factors = get_prime_factors(n, primes_for_factorization)
        approx = calculate_hardy_littlewood(n, prime_factors)
        asymptotic_values.append(approx)
    print("Calculation complete.")

    print(f"Generating plot and saving to {plot_filename}...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(15, 10))

    # Plot real data
    ax.plot(n_values, g_n_values, 'o', markersize=1, color='cyan', alpha=0.6, label='Datos Reales g(N)')
    
    # Plot asymptotic approximation
    ax.plot(n_values, asymptotic_values, '-', color='magenta', linewidth=2, label='Aproximación Asintótica (Hardy-Littlewood)')

    ax.set_title('g(N) vs. Aproximación Asintótica', fontsize=20, color='white')
    ax.set_xlabel('Número Par (N)', fontsize=16, color='white')
    ax.set_ylabel('Número de Pares de Primos g(N)', fontsize=16, color='white')
    ax.grid(True, linestyle='--', alpha=0.2)
    ax.legend(loc='upper left')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to {plot_filename}")

if __name__ == "__main__":
    main()
