import os
from urllib.parse import urlparse
from collections import Counter
from math import log2
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple, Optional

OUTPUT_FILE = "results2.txt"
IMG_FOLDER = "img2"


def get_text_from_url(url: str) -> Optional[str]:
    """
    Downloads raw HTML content from the specified URL, sanitizes it by removing
    script and style components, and returns clean, stripped text block.
    """
    try:
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            )
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Decompose scripting and styling tags
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)

        return clean_text

    except requests.RequestException as e:
        print(f"Error: Failed to fetch webpage content. Details: {e}")
        return None


def write_to_file(content: str) -> None:
    """Writes the analysis report to the output file."""
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(content + "\n\n")


def analyze_text(text: str, source_url: str) -> List[Tuple[str, int, float]]:
    """
    Analyzes the text frequency counts, Shannon entropy, and total information content.
    Appends the calculated report to results2.txt and returns the symbol frequency profiles.
    """
    n = len(text)
    if n == 0:
        print("Error: Empty website content. Nothing to analyze.")
        return []

    counter = Counter(text)
    inf_list = [(char, freq, freq / n) for char, freq in counter.items()]
    inf_list.sort(key=lambda x: x[1], reverse=True)

    # Shannon Entropy Calculation
    H = -sum(p * log2(p) for _, _, p in inf_list if p > 0)
    I = H * n

    header = f"=== Website Analysis: {source_url} ==="
    stats = [
        header,
        f"Total text length: {n} symbols",
        "-" * 40,
        "Symbol | Frequency | Probability",
        "-" * 40
    ]
    for char, freq, p in inf_list:
        stats.append(f"{repr(char):<7}| {freq:<10}| {p:.6f}")

    stats.append("-" * 40)
    stats.append(f"Entropy (H): {H:.4f} bits/symbol")
    stats.append(f"Information Quantity (I): {I:.2f} bits (~{I / 8 / 1024:.2f} KB)")

    report = "\n".join(stats)
    print(report)
    write_to_file(report)

    return inf_list


def save_char_distribution_plot(inf_list: List[Tuple[str, int, float]], source_url: str) -> None:
    """Generates and saves a histogram for the top 30 most frequent characters."""
    if not inf_list:
        print("No character statistics available to plot.")
        return

    top_n = 30
    inf_list_top = inf_list[:top_n]

    chars = [repr(item[0]) for item in inf_list_top]
    counts = [item[1] for item in inf_list_top]

    plt.figure(figsize=(15, 8))
    plt.bar(chars, counts, color='skyblue')
    plt.xlabel("Symbols", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.title(f"Top {top_n} Character Frequencies on Site:\n{source_url}", fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    parsed_url = urlparse(source_url)
    filename_prefix = parsed_url.netloc.replace('.', '_')
    filename = f"{filename_prefix}_char_distribution.png"
    full_path = os.path.join(IMG_FOLDER, filename)

    plt.savefig(full_path, dpi=200)
    plt.close()
    print(f"Character frequency chart saved to: {os.path.abspath(full_path)}")


def main() -> None:
    os.makedirs(IMG_FOLDER, exist_ok=True)

    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        print(f"Cleaned legacy output file: '{OUTPUT_FILE}'")

    while True:
        url = input("\nEnter website URL for evaluation (or '0' to exit): ").strip()
        if url == '0':
            print("Exiting application.")
            break

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            print(f"Autocorrected URL target: {url}")

        print("Fetching and processing data from site...")
        text = get_text_from_url(url)

        if text:
            inf_list = analyze_text(text, url)
            save_char_distribution_plot(inf_list, url)
        else:
            print(f"Could not load content from {url}. Please try another website.")


if __name__ == "__main__":
    main()