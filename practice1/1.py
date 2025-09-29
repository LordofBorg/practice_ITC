import json
from math import log2
from collections import Counter
import matplotlib.pyplot as plt
import os

# --- ЗМІНА 1: Визначення констант для папок ---
OUTPUT_FILE = "results.txt"
IMG_FOLDER = "img"  # Назва папки для зображень


def write_to_file(content):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(content + "\n")


def analyze_text(text, lang, variant):
    n = len(text)
    counter = Counter(text)
    if n == 0:
        return [], 0.0, 0.0
    inf_list = [(ch, freq, freq / n) for ch, freq in counter.items()]
    inf_list.sort(key=lambda x: x[1])

    H = -sum(p * log2(p) for _, _, p in inf_list if p > 0)
    I = H * n

    header = f"\n=== {lang} ({variant}) ==="
    stats = [header, f"Довжина тексту: {n} символів", "Символ | Кількість | Ймовірність"]
    for ch, freq, p in inf_list:
        stats.append(f"{repr(ch):6} | {freq:9} | {p:.5f}")
    stats.append(f"Ентропія (H): {H:.4f} біт/символ")
    stats.append(f"Кількість інформації: {I:.2f} біт (~{I / 8:.2f} байт)")

    print("\n".join(stats))
    write_to_file("\n".join(stats))

    return inf_list, H, I


def save_distribution(inf_list, lang, variant):
    if not inf_list:
        print(f"Немає символів для гістограми: {lang} ({variant})")
        return
    X = [item[0] for item in inf_list]
    Y = [item[1] for item in inf_list]
    plt.figure(figsize=(8, 5))
    plt.bar(X, Y)
    plt.xlabel("Символ")
    plt.ylabel("Кількість")
    plt.title(f"Розподіл символів ({lang}, {variant})")
    plt.grid(True)

    filename = f"{lang}_{variant}_hist.png".replace(" ", "_")
    # --- ЗМІНА 2: Формування повного шляху до файлу ---
    full_path = os.path.join(IMG_FOLDER, filename)

    plt.tight_layout()
    plt.savefig(full_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Графік збережено у файл: {os.path.abspath(full_path)}")


def save_info_comparison(results):
    if not results:
        print("Немає результатів для побудови загального графіка.")
        return
    langs = [f"{lang} ({variant})" for lang, variant, _, _ in results]
    infos = [I for _, _, _, I in results]

    plt.figure(figsize=(10, 6))
    plt.bar(langs, infos)
    plt.xlabel("Мова/Варіант")
    plt.ylabel("Кількість інформації (біти)")
    plt.title("Порівняння кількості інформації у текстах")
    plt.grid(axis="y")
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()

    filename = "info_comparison.png"
    # --- ЗМІНА 3: Формування повного шляху до файлу ---
    full_path = os.path.join(IMG_FOLDER, filename)

    plt.savefig(full_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Загальний графік збережено у файл: {os.path.abspath(full_path)}")


def save_individual_comparisons(results):
    print("\nСтворення окремих графіків порівняння для кожної мови...")
    grouped_data = {}
    for lang, variant, H, I in results:
        if lang not in grouped_data:
            grouped_data[lang] = {}
        grouped_data[lang][variant] = I

    if 'Користувацький' in grouped_data:
        del grouped_data['Користувацький']

    for lang, variants_data in grouped_data.items():
        info_v1 = variants_data.get('variant1', 0)
        info_v3 = variants_data.get('variant3', 0)

        if info_v1 == 0 or info_v3 == 0:
            print(f"Пропуск графіка для '{lang}', оскільки дані для одного з варіантів відсутні.")
            continue

        variants_labels = ["Зв'язний (variant1)", "Незв'язний (variant3)"]
        info_values = [info_v1, info_v3]

        fig, ax = plt.subplots(figsize=(7, 6))
        bars = ax.bar(variants_labels, info_values, color=['cornflowerblue', 'lightcoral'])
        ax.set_ylabel('Кількість інформації (біти)')
        ax.set_title(f"Порівняння для мови: {lang}")
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.bar_label(bars, fmt='%.0f', padding=3)
        fig.tight_layout()

        filename = f"comparison_{lang}.png".replace(" ", "_")
        # --- ЗМІНА 4: Формування повного шляху до файлу ---
        full_path = os.path.join(IMG_FOLDER, filename)

        plt.savefig(full_path, dpi=200)
        plt.close(fig)
        print(f"Графік для мови '{lang}' збережено у файл: {os.path.abspath(full_path)}")


def load_test_texts(filename="texts.json"):
    if not os.path.exists(filename):
        print("Файл texts.json не знайдено!")
        return {}
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    test_texts = load_test_texts()
    results = []

    # --- ЗМІНА 5: Створення папки для зображень, якщо вона не існує ---
    os.makedirs(IMG_FOLDER, exist_ok=True)

    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    while True:
        print("\nВиберіть дію:")
        print("1. Ввести текст вручну")
        print("2. Використати тестові варіанти з JSON (варіант 1 або 3 для всіх мов)")
        print("0. Вихід")
        choice = input("Ваш вибір: ").strip()

        if choice == "1":
            text = input("Введіть свій текст:\n")
            inf_list, H, I = analyze_text(text, "Користувацький", "manual")
            save_distribution(inf_list, "Користувацький", "manual")
            results.append(("Користувацький", "manual", H, I))

        elif choice == "2":
            if not test_texts:
                print("Немає текстів у JSON!")
                continue

            print("\nОберіть варіант для всіх мов:")
            print("1. variant1")
            print("2. variant3")
            var_choice = input("Оберіть варіант (1 або 3): ").strip()
            variant = "variant1" if var_choice == "1" else "variant3"

            batch_results = []
            for lang, variants in test_texts.items():
                text = variants.get(variant, "")
                if text and text.strip():
                    inf_list, H, I = analyze_text(text, lang, variant)
                    save_distribution(inf_list, lang, variant)
                    batch_results.append((lang, variant, H, I))
                else:
                    print(f"{lang}: текст для {variant} відсутній або порожній!")

            if batch_results:
                results.extend(batch_results)

        elif choice == "0":
            if results:
                save_info_comparison(results)
                save_individual_comparisons(results)
            print("Вихід з програми.")
            break

        else:
            print("Неправильний вибір. Спробуйте ще раз.")


if __name__ == "__main__":
    main()