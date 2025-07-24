import pandas as pd
import matplotlib.pyplot as plt
import os
import re

CSV_FILE = 'test_suite_results.csv'
OUTPUT_DIR = 'risultati_analisi'
LATEX_TABLES_FILE = 'report_tabelle.tex'

plt.style.use('seaborn-v0_8-whitegrid')

COLOR_PALETTE = ['#0072B2', '#D55E00', '#009E73', '#CC79A7']
MARKER_STYLES = ['o', 's', '^', 'D']


def sanitize_filename(name: str) -> str:
    name = name.replace(' ', '_').replace('(', '').replace(')', '')
    return re.sub(r'[^a-zA-Z0-9_]', '', name).lower()


def generate_latex_table(df: pd.DataFrame, caption: str, label: str, values_col: str, latex_file_handle,
                         index_col: str = 'StringLength',
                         columns_col: str = 'Algorithm'):
    print(f"Generazione tabella LaTeX per: {caption}...")
    try:
        pivot_df = df.pivot_table(index=index_col, columns=columns_col, values=values_col)

        pivot_df.columns.name = None
        if pd.api.types.is_numeric_dtype(pivot_df.index):
            pivot_df.index = pivot_df.index.astype(int)

        formatted_pivot = pivot_df.map(lambda x: f'{x:.6f}' if isinstance(x, float) else x)

        column_format = 'l|' + '|'.join(['r'] * len(formatted_pivot.columns))

        latex_code = formatted_pivot.to_latex(
            caption=caption,
            label=f'tab:{sanitize_filename(label)}',
            column_format=column_format,
            header=True,
            bold_rows=True,
            position='H'
        )

        latex_file_handle.write("\\begin{center}\n")
        latex_file_handle.write(latex_code)
        latex_file_handle.write("\\end{center}\n\n")

    except Exception as e:
        print(f"Impossibile generare la tabella pivot per '{caption}'. Errore: {e}")


def generate_correctness_latex(df: pd.DataFrame, caption: str, label: str, latex_file_handle):
    print(f"Generazione tabella LaTeX per: {caption}...")
    try:
        display_df = df[['TestCase', 'Algorithm', 'Status']].copy()
        pivot_df = display_df.pivot(index='TestCase', columns='Algorithm', values='Status')

        pivot_df.columns.name = None

        column_format = 'l|' + '|'.join(['c'] * len(pivot_df.columns))

        latex_code = pivot_df.to_latex(
            caption=caption,
            label=f'tab:{sanitize_filename(label)}',
            column_format=column_format,
            header=True,
            bold_rows=True,
            position='H'
        )

        latex_file_handle.write("\\begin{center}\n")
        latex_file_handle.write(latex_code)
        latex_file_handle.write("\\end{center}\n\n")

    except Exception as e:
        print(f"Impossibile generare la tabella di correttezza. Errore: {e}")


def plot_performance(df: pd.DataFrame, title: str, y_label: str, filename: str, use_log_scale: bool = False):
    print(f"Generazione grafico: {title}...")
    fig, ax = plt.subplots(figsize=(12, 8))

    algorithms = sorted(df['Algorithm'].unique())
    for i, algo_name in enumerate(algorithms):
        group = df[df['Algorithm'] == algo_name]
        ax.plot(group['StringLength'], group[y_label],
                marker=MARKER_STYLES[i % len(MARKER_STYLES)],
                linestyle='-',
                label=algo_name,
                color=COLOR_PALETTE[i % len(COLOR_PALETTE)])

    final_title = title
    if use_log_scale:
        ax.set_yscale('log')
        final_title += " (Scala Logaritmica)"

    ax.set_title(final_title, fontsize=16, pad=20)
    ax.set_xlabel('Lunghezza delle Stringhe (n)', fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_xlim(left=0)

    ax.legend(title='Algoritmo', fontsize=10)
    ax.grid(True, which="both", ls="--")
    output_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Grafico salvato in: {output_path}")


def plot_alphabet_impact_single_algo(df: pd.DataFrame, algorithm_name: str, y_label: str, filename: str):
    metric_name = "Tempo" if "Time" in y_label else "Memoria"
    title = f"Impatto Alfabeto su {metric_name} ({algorithm_name})"
    print(f"Generazione grafico: {title}...")
    pivot_df = df.pivot_table(index='StringLength', columns='Alphabet', values=y_label)
    fig, ax = plt.subplots(figsize=(10, 7))
    pivot_df.plot(kind='bar', ax=ax, width=0.6, color=COLOR_PALETTE)
    ax.set_title(title, fontsize=16, pad=20)
    ax.set_xlabel('Lunghezza Stringa', fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.tick_params(axis='x', rotation=0)
    ax.legend(title='Alfabeto', fontsize=10)
    ax.grid(axis='y', linestyle='--')
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    print(f"Grafico salvato in: {output_path}")


def main():
    if not os.path.exists(CSV_FILE):
        print(f"Errore: File '{CSV_FILE}' non trovato.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_csv(CSV_FILE)

    latex_output_path = os.path.join(OUTPUT_DIR, LATEX_TABLES_FILE)

    latex_preamble = r"""
\documentclass[a4paper, 11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{geometry}
\usepackage{float}

\geometry{a4paper, margin=1in}

\title{Analisi Sperimentale di Algoritmi per Longest Common Subsequence}
\author{Francesco}
\date{\today}

\begin{document}
\maketitle
\tableofcontents
\newpage
"""
    latex_postamble = r"\end{document}"

    with open(latex_output_path, 'w', encoding='utf-8') as latex_file:
        print(f"Le tabelle LaTeX verranno salvate in: {os.path.abspath(latex_output_path)}")

        latex_file.write(latex_preamble)

        latex_file.write("\n\\section{Test di Correttezza}\n")
        correctness_df = df[df['TestScenario'] == 'Correttezza'].copy()
        if not correctness_df.empty:
            generate_correctness_latex(correctness_df, 'Risultati dei test di correttezza', 'correttezza_risultati',
                                       latex_file)

        latex_file.write("\n\\section{Test di Performance - Confronto}\n")
        exp_df = df[df['TestScenario'] == 'Performance Confronto - Esponenziale'].copy()
        poly_df = df[df['TestScenario'] == 'Performance Confronto - Polinomiale'].copy()

        if not exp_df.empty:
            latex_file.write("\n\\subsection{Algoritmi Esponenziali}\n")
            plot_performance(exp_df, 'Confronto Performance (Tempo) - Algoritmi Esponenziali', 'MedianTime_s',
                             'plot_confronto_tempo_esponenziale_lineare.png', use_log_scale=False)
            plot_performance(exp_df, 'Confronto Performance (Memoria) - Algoritmi Esponenziali', 'PeakMemory_MB',
                             'plot_confronto_memoria_esponenziale.png', use_log_scale=False)
            generate_latex_table(exp_df, 'Tempi mediani (s) per confronto algoritmi esponenziali',
                                 'confronto_tempi_esponenziali', 'MedianTime_s', latex_file)
            generate_latex_table(exp_df, 'Picco di memoria (MB) per confronto algoritmi esponenziali',
                                 'confronto_memoria_esponenziale', 'PeakMemory_MB', latex_file)

        if not poly_df.empty:
            latex_file.write("\n\\subsection{Algoritmi Polinomiali}\n")
            plot_performance(poly_df, 'Confronto Performance (Tempo) - Algoritmi Polinomiali', 'MedianTime_s',
                             'plot_confronto_tempo_polinomiale.png')
            plot_performance(poly_df, 'Confronto Performance (Memoria) - Algoritmi Polinomiali', 'PeakMemory_MB',
                             'plot_confronto_memoria_polinomiale.png')
            generate_latex_table(poly_df, 'Tempi mediani (s) per confronto algoritmi polinomiali',
                                 'confronto_tempi_polinomiali', 'MedianTime_s', latex_file)
            generate_latex_table(poly_df, 'Picco di memoria (MB) per confronto algoritmi polinomiali',
                                 'confronto_memoria_polinomiali', 'PeakMemory_MB', latex_file)

        latex_file.write("\n\\section{Test sull'Impatto dell'Alfabeto}\n")
        alphabet_df = df[df['TestScenario'] == 'Impatto Alfabeto'].copy()
        if not alphabet_df.empty:
            for algo_name in sorted(alphabet_df['Algorithm'].unique()):
                latex_file.write(f"\n\\subsection{{{algo_name}}}\n")
                group = alphabet_df[alphabet_df['Algorithm'] == algo_name]
                sanitized_name = sanitize_filename(algo_name)

                plot_alphabet_impact_single_algo(group, algo_name, 'MedianTime_s',
                                                 f'plot_impatto_alfabeto_tempo_{sanitized_name}.png')
                plot_alphabet_impact_single_algo(group, algo_name, 'PeakMemory_MB',
                                                 f'plot_impatto_alfabeto_memoria_{sanitized_name}.png')

                generate_latex_table(group, f'Impatto Alfabeto ({algo_name}) - Tempo (s)',
                                     f'impatto_alfabeto_tempo_{sanitize_filename(algo_name)}', 'MedianTime_s',
                                     latex_file, columns_col='Alphabet')
                generate_latex_table(group, f'Impatto Alfabeto ({algo_name}) - Memoria (MB)',
                                     f'impatto_alfabeto_memoria_{sanitize_filename(algo_name)}', 'PeakMemory_MB',
                                     latex_file, columns_col='Alphabet')

        latex_file.write(latex_postamble)

    print(f"\nAnalisi completata. Tutti i grafici sono stati salvati nella cartella: '{os.path.abspath(OUTPUT_DIR)}'")


if __name__ == '__main__':
    main()
