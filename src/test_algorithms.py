import time
import random
import string
import statistics
import csv
import os
import tracemalloc

from lcs_algorithms import (
    lcs_memoized,
    lcs_bottom_up,
    lcs_recursive,
    lcs_brute_force
)

# Dizionario algoritmi
ALGORITHMS = {
    "Forza Bruta": lcs_brute_force,
    "Ricorsivo": lcs_recursive,
    "Memoized": lcs_memoized,
    "Bottom-up": lcs_bottom_up,
}


# --- FUNZIONI DI SUPPORTO ---
def generate_random_string(length: int, alphabet: str) -> str:
    """Genera una stringa casuale di data lunghezza da dato alfabeto"""
    if length == 0:
        return ""
    return ''.join(random.choice(alphabet) for i in range(length))


def run_single_experiment(algorithm_func, X: str, Y: str):
    """
    Esegue un singolo esperimento per un dato algoritmo. Misura tempo e memoria.
    Restituisce una tupla contenente (result_lcs, execution_time_s, peak_memory_mb).
    """
    # inizia il tracciamento della memoria
    tracemalloc.start()

    # misura il tempo di esecuzione dell'algoritmo
    start_time = time.perf_counter()
    result_lcs = algorithm_func(X, Y)
    end_time = time.perf_counter()

    # ottiene il picco di memoria utilizzato e ferma il tracciamento
    _, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    execution_time_s = end_time - start_time

    peak_memory_mb = peak_mem / 10 ** 6
    return result_lcs, execution_time_s, peak_memory_mb     # converte da byte a megabyte


def _is_subsequence(sub: str, main_str: str) -> bool:
    """
    Funzione di supporto per verificare se 'sub' è una sottosequenza di 'main_str'.
    """
    i = 0
    j = 0

    while i < len(sub) and j < len(main_str):
        if sub[i] == main_str[j]:
            i += 1  # se i caratteri corrispondono, aumento l'indice di sub
        j += 1      # in ogni caso aumento quello di main_str

    # se ho trovato tutti i caratteri di sub, l'indice i deve essere pari alla sua lunghezza
    return i == len(sub)


# --- SUITE DI TEST ---

def run_correctness_tests():
    """
    Esegue test di correttezza per verificare che tutti gli algoritmi producano una LCS valida.
    """
    print("--- Inizio Test di Correttezza ---")
    results = []
    # lista di casi di test, ciascuno definito con un dizionario
    test_cases = [
        {"X": "AGGTAB", "Y": "GXTXAYB", "expected": "GTAB", "case": "Classico"},
        {"X": "ABCDE", "Y": "ACE", "expected": "ACE", "case": "Una stringa è sottosequenza dell'altra"},
        {"X": "ABC", "Y": "XYZ", "expected": "", "case": "Nessun carattere comune"},
        {"X": "ABCDEFG", "Y": "ABCDEFG", "expected": "ABCDEFG", "case": "Stringhe identiche"},
        {"X": "", "Y": "XYZ", "expected": "", "case": "Prima stringa vuota"},
        {"X": "ABC", "Y": "", "expected": "", "case": "Seconda stringa vuota"},
        {"X": "", "Y": "", "expected": "", "case": "Entrambe le stringhe vuote"},
        {"X": "ABCBDAB", "Y": "BDCABA", "expected_len": 4, "case": "LCS multipli possibili (BCAB, BDAB)"}
    ]

    for case_data in test_cases:
        X, Y, case_name = case_data["X"], case_data["Y"], case_data["case"]
        # se "expected_len" non fosse specificato, lo calcolo a partire da "expected"
        expected_len = case_data.get('expected_len', len(case_data.get('expected', '')))
        print(f"\nCaso di test: {case_name} (X='{X}', Y='{Y}')")
        # itera su tutti gli algoritmi definiti nel dizionario ALGORITHMS
        for algo_name, algo_func in ALGORITHMS.items():
            try:
                lcs_result, _, _ = run_single_experiment(algo_func, X, Y)
                actual_len = len(lcs_result)
                # per essere corretta deve avere lunghezza corrispondente a quella attesa
                # e la lcs trovata deve essere sottosequenza di entrambe le stringhe di partenza
                is_valid_subsequence = _is_subsequence(lcs_result, X) and _is_subsequence(lcs_result, Y)
                status = "Pass" if actual_len == expected_len and is_valid_subsequence else "Fail"
                print(
                    f"  - {algo_name:<12}: Lunghezza trovata = {actual_len}, Attesa = {expected_len}, "
                    f"Valida = {is_valid_subsequence} -> {status}")
                results.append(
                    {"TestScenario": "Correttezza", "Algorithm": algo_name, "TestCase": case_name, "Status": status})
            except Exception as e:
                print(f"  - {algo_name:<12}: ERRORE -> {e}")
                results.append(
                    {"TestScenario": "Correttezza", "Algorithm": algo_name, "TestCase": case_name, "Status": "Error"})
    print("\n--- Fine Test di Correttezza ---")
    return results


def run_comparison_performance_tests():
    """
    Esegue test di performance per confrontare gli algoritmi tra loro.
    Gli scenari sono separati in base alla complessità attesa: esponenziale (Forza Bruta, Ricorsivo)
    e polinomiale (Memoized, Bottom-up), usando stringhe di dimensioni appropriate per ciascun gruppo.
    Per ogni combinazione di algoritmo e lunghezza, l'esperimento viene ripetuto più volte (num_repetitions)
    e i risultati vengono aggregati calcolando la mediana, per ridurre l'impatto di eventuali outlier.
    """
    print("\n--- Inizio Test di Performance di Confronto ---")
    results = []
    # separo i test in piu scenari a seconda del tipo di algoritmo
    test_configs = [
        {
            "scenario_name": "Performance Confronto - Esponenziale",
            "algorithms_to_run": ["Forza Bruta", "Ricorsivo"],
            "string_lengths": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "num_repetitions": 3,
            "alphabet": string.ascii_lowercase,
        },
        {
            "scenario_name": "Performance Confronto - Polinomiale",
            "algorithms_to_run": ["Memoized", "Bottom-up"],
            "string_lengths": [0, 50, 100, 150, 200, 250, 300, 350, 400],
            "num_repetitions": 3,
            "alphabet": string.ascii_lowercase,
        },
    ]
    for config in test_configs:
        scenario = config["scenario_name"]
        print(f"\nEsecuzione scenario: {scenario}")
        for algo_name in config["algorithms_to_run"]:
            for length in config["string_lengths"]:
                times, memories = [], []
                print(f" - Test di {algo_name} con lunghezza {length}")
                for i in range(config["num_repetitions"]):
                    X = generate_random_string(length, config["alphabet"])
                    Y = generate_random_string(length, config["alphabet"])
                    _, exec_time, peak_mem = run_single_experiment(ALGORITHMS[algo_name], X, Y)
                    times.append(exec_time)
                    memories.append(peak_mem)
                results.append({"TestScenario": scenario, "Algorithm": algo_name, "StringLength": length,
                                "MedianTime_s": statistics.median(times), "PeakMemory_MB": statistics.median(memories)})
    print("\n--- Fine Test di Performance di Confronto ---")
    return results


def run_alphabet_impact_tests():
    """
    Analizza se la dimensione dell'alfabeto (es: DNA con 4 caratteri vs A-Z con 26)
    influisce sulle performance degli algoritmi. L'ipotesi è che un alfabeto più piccolo
    aumenti la probabilità di trovare caratteri comuni, influenzando potenzialmente
    il tempo e la memoria utilizzati.
    """
    print("\n--- Inizio Test Impatto Alfabeto ---")
    results = []
    alphabets = {"DNA (4)": "ACTG", "A-Z (26)": string.ascii_uppercase}
    configs = [
        {"algorithms": ["Forza Bruta", "Ricorsivo"], "lengths": [10, 11, 12]},
        {"algorithms": ["Memoized", "Bottom-up"], "lengths": [100, 200, 300]}
    ]
    num_repetitions = 5
    for config in configs:
        for algo_name in config["algorithms"]:
            print(f"Test algoritmo: {algo_name}")
            for length in config["lengths"]:
                for alphabet_name, alphabet in alphabets.items():
                    times, memories = [], []
                    print(f"  - lunghezza: {length}, alfabeto: {alphabet_name}")
                    for _ in range(num_repetitions):
                        X = generate_random_string(length, alphabet)
                        Y = generate_random_string(length, alphabet)
                        _, exec_time, peak_mem = run_single_experiment(ALGORITHMS[algo_name], X, Y)
                        times.append(exec_time)
                        memories.append(peak_mem)
                    results.append({"TestScenario": "Impatto Alfabeto", "Algorithm": algo_name, "StringLength": length,
                                    "MedianTime_s": statistics.median(times),
                                    "PeakMemory_MB": statistics.median(memories), "Alphabet": alphabet_name})
    print("\n--- Fine Test Impatto Alfabeto ---")
    return results


def main():
    """
    Funzione principale che fa partire tutte le suite di test.
    I risultati vengono salvati su un singolo file csv.
    """
    all_results = (
            run_correctness_tests() +
            run_comparison_performance_tests() +
            run_alphabet_impact_tests()
    )
    output_csv_file = 'test_suite_results.csv'
    if not all_results:
        print("Nessun risultato da salvare")
        return

    # trovo tutti i possibili campi dai vari risultati, assegnando loro una colonna del file
    all_fieldnames = set().union(*(d.keys() for d in all_results))
    preferred_order = [
        "TestScenario", "Algorithm", "TestCase", "StringLength", "Status",
        "MedianTime_s", "PeakMemory_MB", "Alphabet", "ExpectedLCS_Length",
        "ActualLCS_Length", "String1", "String2", "ErrorDetails"
    ]
    fieldnames = [field for field in preferred_order if field in all_fieldnames]
    fieldnames += sorted([field for field in all_fieldnames if field not in preferred_order])

    try:
        with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval='N/A')
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\nEsperimenti conclusi. Risultati salvati in {os.path.abspath(output_csv_file)}")
    except IOError as e:
        print(f"\nErrore durante la scrittura del file CSV: {e}")


if __name__ == "__main__":
    main()
