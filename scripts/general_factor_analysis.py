import pandas as pd
import numpy as np
import sys

# --- Constantes y Funciones Base ---

C2 = 0.6601618158  # Constante de primos gemelos

def hardy_littlewood_naive(N):
    """Aproximación ingenua: 2 * C₂ * N / (ln N)²"""
    if N <= 4: return 1
    return 2 * C2 * N / (np.log(N) ** 2)

def analyze_data(filepath):
    """Carga y prepara los datos para el análisis."""
    print(f"Procesando archivo: {filepath}")
    df = pd.read_csv(filepath)
    df = df.rename(columns={'g(N)_real': 'g_actual'})
    
    print("Calculando aproximación ingenua de Hardy-Littlewood...")
    df['hl_naive'] = df['N'].apply(hardy_littlewood_naive)
    df['ratio_naive'] = df['g_actual'] / df['hl_naive']
    
    print("Datos listos para el análisis.")
    return df

# --- Función de Análisis Generalizada ---

def analyze_prime_factor(df, p):
    """
    Analiza el efecto de un divisor primo 'p' en los ratios de Goldbach.
    Compara el factor empírico con el teórico (p-1)/(p-2).
    """
    print(f"\n--- Análisis para el Primo p = {p} ---")
    
    # 1. Separar datos
    df['divisible_by_p'] = df['N'] % p == 0
    div_by_p = df[df['divisible_by_p']]
    not_div_by_p = df[~df['divisible_by_p']]
    
    # 2. Calcular medias
    mean_p = div_by_p['ratio_naive'].mean()
    mean_not_p = not_div_by_p['ratio_naive'].mean()
    
    print(f"Media del ratio (N divisible por {p}):   {mean_p:.4f}")
    print(f"Media del ratio (N NO divisible por {p}): {mean_not_p:.4f}")
    
    # 3. Calcular factor empírico
    if mean_not_p == 0: 
        print("No se puede calcular el factor empírico (media de no divisibles es cero).")
        return
        
    f_p_empirical = mean_p / mean_not_p
    print(f"\nFactor Empírico f_{p}: {f_p_empirical:.4f}")
    
    # 4. Calcular factor teórico
    f_p_theoretical = (p - 1) / (p - 2)
    print(f"Factor Teórico (p-1)/(p-2): {f_p_theoretical:.4f}")
    
    # 5. Comparar
    difference = abs(f_p_empirical - f_p_theoretical)
    error_percent = (difference / f_p_theoretical) * 100
    print(f"\nDiferencia entre empírico y teórico: {difference:.4f} ({error_percent:.2f}% de error)")

# --- Ejecución Principal ---

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Proporciona la ruta al archivo CSV de entrada.")
        sys.exit(1)
        
    INPUT_FILE = sys.argv[1]
    
    df_analysis = analyze_data(INPUT_FILE)
    
    primes_to_analyze = [3, 5, 7]
    
    print("\n=== ANÁLISIS GENERALIZADO DE FACTORES DE CORRECCIÓN (HIPÓTESIS DEL ESPEJO) ===")
    for prime in primes_to_analyze:
        analyze_prime_factor(df_analysis, prime)