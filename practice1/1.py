import json
from math import log2
from collections import Counter
import matplotlib.pyplot as plt
import os
from typing import List, Tuple, Dict, Any

OUTPUT_FILE = "results.txt"
IMG_FOLDER = "img"


def write_to_file(content: str) -> None:
    """Appends the given content to the results output file."""
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(content + "\n")


def analyze_text(text: str, lang: str, variant: str) -> Tuple[List[Tuple[str, int, float]], float, float]:
    """
    Calculates character frequencies, Shannon entropy, and total information amount.
    Saves the text statistics into results.txt and returns detailed character frequency profiles.
    """
    n = len(text)
    counter = Counter(text)
    if n == 0:
        return [], 0.0, 0.0

    # Create character info: (character, frequency count, probability)
    inf_list = [(ch, freq, freq / n) for ch, freq in counter.items()]
    inf_list.sort(key=lambda x: x[1])

    # Calculate Shannon Entropy
    H = -sum(p * log2(p) for _, _, p in inf_list if p > 0)
    I = H * n

    header = f"\n=== {lang} ({variant}) ==="
    stats = [header, f"Text length: {n} characters", "Symbol | Frequency | Probability"]
    for ch, freq, p in inf_list:
        stats.append(f"{repr(ch):6} | {freq:9} | {p:.5f}")
    stats.append(f"Entropy (H): {H:.4f} bits/symbol")
    stats.append(f"Information amount (I): {I:.2f} bits (~{I / 8:.2f} bytes)")

    print("\n".join(stats))
    write_to_file("\n".join(stats))

    return inf_list, H, I


def save_distribution(inf_list: List[Tuple[str, int, float]], lang: str, variant: str) -> None:
    """Generates and saves a histogram of the character frequency distribution."""
    if not inf_list:
        print(f"No characters found for distribution: {lang} ({variant})")
        return

    X = [item[0] for item in inf_list]
    Y = [item[1] for item in inf_list]

    plt.figure(figsize=(8, 5))
    plt.bar(X, Y)
    plt.xlabel("Symbol")
    plt.ylabel("Frequency")
    plt.title(f"Character Distribution ({lang}, {variant})")
    plt.grid(True)

    filename = f"{lang}_{variant}_hist.png".replace(" ", "_")
    full_path = os.path.join(IMG_FOLDER, filename)

    plt.tight_layout()
    plt.savefig(full_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Chart saved to: {os.path.abspath(full_path)}")


def save_info_comparison(results: List[Tuple[str, str, float, float]]) -> None:
    """Generates and saves a comparison bar chart of total information across all texts."""
    if not results:
        print("No results available for comparison charts.")
        return

    langs = [f"{lang} ({variant})" for lang, variant, _, _ in results]
    infos = [I for _, _, _, I in results]

    plt.figure(figsize=(10, 6))
    plt.bar(langs, infos)
    plt.xlabel("Language / Variant")
    plt.ylabel("Information quantity (bits)")
    plt.title("Information Quantity Comparison across Texts")
    plt.grid(axis="y")
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()

    filename = "info_comparison.png"
    full_path = os.path.join(IMG_FOLDER, filename)

    plt.savefig(full_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Overall comparison chart saved to: {os.path.abspath(full_path)}")


def save_individual_comparisons(results: List[Tuple[str, str, float, float]]) -> None:
    """Generates and saves comparison charts for each language comparing Variant 1 and Variant 3."""
    grouped_data = {}
    for lang, variant, H, I in results:
        if lang not in grouped_data:
            grouped_data[lang] = {}
        grouped_data[lang][variant] = I

    if 'User Defined' in grouped_data:
        del grouped_data['User Defined']
    if 'Користувацький' in grouped_data:
        del grouped_data['Користувацький']

    for lang, variants_data in grouped_data.items():
        info_v1 = variants_data.get('variant1', 0)
        info_v3 = variants_data.get('variant3', 0)

        if info_v1 == 0 or info_v3 == 0:
            continue

        variants_labels = ["Connected (variant1)", "Unconnected (variant3)"]
        info_values = [info_v1, info_v3]

        fig, ax = plt.subplots(figsize=(7, 6))
        bars = ax.bar(variants_labels, info_values, color=['cornflowerblue', 'lightcoral'])
        ax.set_ylabel('Information quantity (bits)')
        ax.set_title(f"Information Contrast: {lang}")
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.bar_label(bars, fmt='%.0f', padding=3)
        fig.tight_layout()

        filename = f"comparison_{lang}.png".replace(" ", "_")
        full_path = os.path.join(IMG_FOLDER, filename)

        plt.savefig(full_path, dpi=200)
        plt.close(fig)
        print(f"Comparison chart for '{lang}' saved to: {os.path.abspath(full_path)}")


def load_test_texts(filename: str = "texts.json") -> Dict[str, Any]:
    """Loads default test text blocks from texts.json."""
    if not os.path.exists(filename):
        print(f"Error: {filename} not found!")
        return {}
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    test_texts = load_test_texts()
    results = []

    os.makedirs(IMG_FOLDER, exist_ok=True)
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    while True:
        print("\nSelect action:")
        print("1. Enter text manually")
        print("2. Run analysis on predefined JSON texts (Variant 1 & 3)")
        print("0. Exit")
        choice = input("Your choice: ").strip()

        if choice == "1":
            text = input("Enter text:\n")
            inf_list, H, I = analyze_text(text, "User Defined", "manual")
            save_distribution(inf_list, "User Defined", "manual")
            results.append(("User Defined", "manual", H, I))

        elif choice == "2":
            if not test_texts:
                print("No texts loaded from JSON database.")
                continue

            print("\nSelect variant for evaluation:")
            print("1. variant1 (Connected texts)")
            print("2. variant3 (Unconnected generated texts)")
            var_choice = input("Your choice (1 or 3): ").strip()
            variant = "variant1" if var_choice == "1" else "variant3"

            batch_results = []
            for lang, variants in test_texts.items():
                text = variants.get(variant, "")
                if text and text.strip():
                    inf_list, H, I = analyze_text(text, lang, variant)
                    save_distribution(inf_list, lang, variant)
                    batch_results.append((lang, variant, H, I))
                else:
                    print(f"Error: {lang} text for {variant} is empty!")

            if batch_results:
                results.extend(batch_results)

        elif choice == "0":
            if results:
                save_info_comparison(results)
                save_individual_comparisons(results)
            print("Exiting application.")
            break

        else:
            print("Invalid selection. Try again.")


if __name__ == "__main__":
    main()