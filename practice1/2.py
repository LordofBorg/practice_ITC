import os
from urllib.parse import urlparse
from collections import Counter
from math import log2
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup

# --- Константи ---
OUTPUT_FILE = "results2.txt"
IMG_FOLDER = "img2"  # Назва папки для зображень


def get_text_from_url(url):
    try:
        # Додаємо User-Agent, щоб імітувати запит від браузера
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Генерує помилку для кодів 4xx/5xx

        # Використовуємо 'html.parser' - вбудований парсер
        soup = BeautifulSoup(response.text, 'html.parser')

        # Видаляємо теги script та style разом з їх вмістом
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        # Отримуємо текст і очищуємо його від зайвих пробілів
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)

        return clean_text

    except requests.RequestException as e:
        print(f"Помилка: Не вдалося завантажити сторінку. {e}")
        return None


def write_to_file(content):
    """Записує контент у вихідний файл."""
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(content + "\n\n")


def analyze_text(text, source_url):
    """
    Аналізує текст: розраховує частоту символів, ентропію та кількість інформації.
    """
    n = len(text)
    if n == 0:
        print("На сайті не знайдено тексту для аналізу.")
        return [], 0.0, 0.0

    counter = Counter(text)
    # Створюємо список з інформацією про кожен символ
    # (символ, кількість, ймовірність)
    inf_list = [(char, freq, freq / n) for char, freq in counter.items()]
    # Сортуємо за кількістю для наочності
    inf_list.sort(key=lambda x: x[1], reverse=True)

    # Розрахунок ентропії за формулою Шеннона
    H = -sum(p * log2(p) for _, _, p in inf_list if p > 0)
    # Розрахунок повної кількості інформації
    I = H * n

    header = f"=== Аналіз сайту: {source_url} ==="
    stats = [
        header,
        f"Загальна довжина тексту: {n} символів",
        "-" * 40,
        "Символ | Кількість | Ймовірність",
        "-" * 40
    ]
    for char, freq, p in inf_list:
        # repr(char) для наочного відображення спецсимволів, як '\n'
        stats.append(f"{repr(char):<7}| {freq:<10}| {p:.6f}")

    stats.append("-" * 40)
    stats.append(f"Ентропія (H): {H:.4f} біт/символ")
    stats.append(f"Кількість інформації (I): {I:.2f} біт (~{I / 8 / 1024:.2f} Кбайт)")

    report = "\n".join(stats)
    print(report)
    write_to_file(report)

    return inf_list


def save_char_distribution_plot(inf_list, source_url):
    """
    Створює та зберігає гістограму розподілу символів.
    """
    if not inf_list:
        print("Немає даних для побудови графіка.")
        return

    # Для кращої візуалізації візьмемо 30 найпопулярніших символів
    top_n = 30
    inf_list_top = inf_list[:top_n]

    chars = [repr(item[0]) for item in inf_list_top]
    counts = [item[1] for item in inf_list_top]

    plt.figure(figsize=(15, 8))
    plt.bar(chars, counts, color='skyblue')
    plt.xlabel("Символи", fontsize=12)
    plt.ylabel("Кількість", fontsize=12)
    plt.title(f"Частота появи {top_n} найпопулярніших символів на сайті:\n{source_url}", fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Створюємо безпечне ім'я файлу з URL
    parsed_url = urlparse(source_url)
    # Використовуємо доменне ім'я, замінюючи точки на підкреслення
    filename_prefix = parsed_url.netloc.replace('.', '_')
    filename = f"{filename_prefix}_char_distribution.png"

    full_path = os.path.join(IMG_FOLDER, filename)

    plt.savefig(full_path, dpi=200)
    plt.close()
    print(f"\nГрафік розподілу символів збережено у файл: {os.path.abspath(full_path)}")


def main():
    """Головна функція програми."""
    # Створюємо папку для зображень, якщо вона не існує
    os.makedirs(IMG_FOLDER, exist_ok=True)

    # Очищуємо файл результатів при новому запуску
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        print(f"Файл '{OUTPUT_FILE}' очищено.")

    while True:
        url = input("\nВведіть URL сайту для аналізу (або '0' для виходу): ").strip()
        if url == '0':
            print("Вихід з програми.")
            break

        # Перевірка, чи введено хоча б щось схоже на URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            print(f"URL автоматично виправлено на: {url}")

        print("\nЗавантаження та обробка даних...")
        text = get_text_from_url(url)

        if text:
            # Якщо текст отримано успішно, аналізуємо його
            inf_list = analyze_text(text, url)
            # Будуємо та зберігаємо графік
            save_char_distribution_plot(inf_list, url)
        else:
            # Якщо текст не отримано, повідомляємо користувача
            print(f"Не вдалося отримати текстовий вміст для {url}. Спробуйте інший сайт.")


if __name__ == "__main__":
    main()