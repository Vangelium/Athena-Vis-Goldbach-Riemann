import csv
import os

def sieve_of_eratosthenes(limit):
    """Generates prime numbers up to a given limit using the Sieve of Eratosthenes."""
    primes = [True] * (limit + 1)
    if limit >= 0:
        primes[0] = False
    if limit >= 1:
        primes[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if primes[i]:
            for multiple in range(i*i, limit + 1, i):
                primes[multiple] = False
    
    prime_numbers = [i for i, is_prime in enumerate(primes) if is_prime]
    return prime_numbers

def calculate_g_n(n, primes_list, primes_set):
    """
    Calculates g(N), the number of ways an even number N can be expressed
    as the sum of two primes.
    """
    count = 0
    # Iterate over the SORTED list of primes to ensure the break condition works
    for p1 in primes_list:
        # We only need to check for primes up to n / 2
        if p1 > n / 2:
            break
        p2 = n - p1
        # Use the set for fast lookups
        if p2 in primes_set:
            # This condition correctly counts unique pairs.
            # Since we iterate p1 up to n/2, p2 will always be >= p1.
            # This avoids double-counting (e.g., 3+7 and 7+3).
            count += 1
    return count

def main():
    """Main function to generate and save Goldbach counts."""
    max_n = 1000000
    output_filename = os.path.join(os.path.dirname(__file__), '..', 'data', 'goldbach_counts.csv')

    print(f"Generating primes up to {max_n}...")
    primes_list = sieve_of_eratosthenes(max_n)
    primes_set = set(primes_list)
    print("Prime generation complete.")

    results = []
    print(f"Calculating g(N) for even numbers up to {max_n}...")
    for n in range(4, max_n + 1, 2):
        g_n = calculate_g_n(n, primes_list, primes_set)
        results.append({'N': n, 'g(N)': g_n})

    print("Calculation complete.")

    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    print(f"Saving data to {output_filename}...")
    with open(output_filename, 'w', newline='') as csvfile:
        fieldnames = ['N', 'g(N)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print("Data saved successfully.")
    print(f"Generated {len(results)} data points.")

if __name__ == "__main__":
    main()