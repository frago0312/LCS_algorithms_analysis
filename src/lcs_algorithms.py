"""
Questo file contiene le implementazioni di quattro diversi algoritmi per risolvere
il problema della Longest Common Subsequence (LCS).
Gli approcci implementati sono:
1. Forza Bruta
2. Ricorsivo Semplice
3. Ricorsivo con Memoization (Top-Down)
4. Bottom-Up (Programmazione Dinamica)
"""


def lcs_brute_force(X: str, Y: str) -> str:
    """
    La versione forza bruta calcola tutte le sottosequenze di una stringa (X)
    e, per ciascuna, verifica se è anche una sottosequenza dell'altra stringa (Y).
    Mantiene traccia della più lunga trovata.
    """
    m = len(X)
    longest_common_subsequence = ""

    # Itera su tutte le 2^m sottosequenze di X (bit mask).
    for i in range(1 << m):
        subsequence = ""
        for j in range(m):
            # Se il j-esimo bit di 'i' è 1, il carattere X[j] fa parte della sottosequenza.
            if (i >> j) & 1:
                subsequence += X[j]

        # Verifica se la sottosequenza generata è anche in Y e se è la più lunga trovata.
        if _is_subsequence(subsequence, Y):
            if len(subsequence) > len(longest_common_subsequence):
                longest_common_subsequence = subsequence

    return longest_common_subsequence


def _is_subsequence(sub: str, main_str: str) -> bool:
    """
    Verifica se 'sub' è una sottosequenza di 'main_str' usando due puntatori.
    """
    i, j = 0, 0  # Puntatori per 'sub' e 'main_str'

    while i < len(sub) and j < len(main_str):
        if sub[i] == main_str[j]:
            i += 1  # Carattere corrispondente trovato
        j += 1  # Avanza sempre su main_str

    return i == len(sub)  # True se tutti i caratteri di 'sub' sono stati trovati



def lcs_recursive(X: str, Y: str) -> str:
    """
    Calcola la LCS usando l'approccio ricorsivo semplice.
    Confronta gli ultimi caratteri delle stringhe: se coincidono, li include nella soluzione e
    continua sui prefissi; altrimenti prova entrambe le possibilità e sceglie la più lunga.
    """
    m, n = len(X), len(Y)

    # Caso base: una delle due stringhe è vuota.
    if m == 0 or n == 0:
        return ""

    # Se gli ultimi caratteri corrispondono, sono parte della LCS.
    if X[m - 1] == Y[n - 1]:
        return lcs_recursive(X[:-1], Y[:-1]) + X[m - 1]
    # Altrimenti, la LCS è la più lunga tra quelle dei due possibili sottoproblemi.
    else:
        lcs1 = lcs_recursive(X, Y[:-1])
        lcs2 = lcs_recursive(X[:-1], Y)
        return lcs1 if len(lcs1) >= len(lcs2) else lcs2


def lcs_memoized(X: str, Y: str) -> str:
    """
    Calcola la LCS in modo ricorsivo top down.
    Evita calcoli ripetuti salvando i risultati intermedi in una cache. Prima di ricorrere a
    nuove chiamate, controlla se il risultato è già noto e, se necessario, lo salva per usi futuri.
    """
    memo = {}  # Cache per i risultati dei sottoproblemi (i, j)

    def _lcs_memo(i, j):
        # Se il risultato è già in cache, lo restituisco.
        if (i, j) in memo:
            return memo[(i, j)]

        # Logica ricorsiva identica alla versione semplice.
        if i == 0 or j == 0:
            return ""
        if X[i - 1] == Y[j - 1]:
            result = _lcs_memo(i - 1, j - 1) + X[i - 1]
        else:
            lcs1 = _lcs_memo(i, j - 1)
            lcs2 = _lcs_memo(i - 1, j)
            result = lcs1 if len(lcs1) >= len(lcs2) else lcs2

        # Salvo il risultato in cache prima di restituirlo.
        memo[(i, j)] = result
        return result

    return _lcs_memo(len(X), len(Y))


def lcs_bottom_up(X: str, Y: str) -> str:
    """
    Calcola la LCS in modo ricorsivo bottom up.
    Risoluzione iterativa tramite una tabella che memorizza le soluzioni dei sottoproblemi.
    Si parte dai casi più semplici e si arriva alla soluzione completa, che viene poi ricostruita.
    """
    m, n = len(X), len(Y)

    # Fase 1: Costruzione della tabella `c` delle lunghezze.
    c = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i - 1] == Y[j - 1]:
                c[i][j] = c[i - 1][j - 1] + 1
            else:
                c[i][j] = max(c[i - 1][j], c[i][j - 1])

    # Fase 2: Ricostruzione della stringa LCS (backtracking).
    # Si parte dall'angolo in basso a destra della tabella e si risale.
    lcs_str = ""
    i, j = m, n
    while i > 0 and j > 0:
        # Se i caratteri corrispondono, fanno parte della LCS.
        if X[i - 1] == Y[j - 1]:
            lcs_str = X[i - 1] + lcs_str
            i -= 1
            j -= 1
        # Altrimenti, ci si sposta nella direzione del valore più grande.
        elif c[i - 1][j] > c[i][j - 1]:
            i -= 1
        else:
            j -= 1

    return lcs_str
