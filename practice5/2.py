import sys
from decimal import Decimal, getcontext
from collections import Counter
from typing import Dict, Tuple

# Set high precision for large text encoding intervals
getcontext().prec = 2100


def preprocess_text(text: str) -> str:
    """Preprocesses text by converting to uppercase."""
    return text.upper()


def calculate_frequencies(text: str) -> Dict[str, Decimal]:
    """Calculates exact probability frequencies for characters in the given text."""
    total_chars = Decimal(len(text))
    if total_chars == 0:
        return {}

    counts = Counter(text)
    probabilities = {char: Decimal(count) / total_chars for char, count in counts.items()}
    return probabilities


def get_cumulative_freqs(probabilities: Dict[str, Decimal]) -> Dict[str, Tuple[Decimal, Decimal]]:
    """Builds a Cumulative Distribution Function (CDF) map of low-high intervals for characters."""
    cdf = {}
    current_low = Decimal('0.0')
    sorted_probs = sorted(probabilities.items(), key=lambda item: item[0])
    for char, prob in sorted_probs:
        cdf[char] = (current_low, current_low + prob)
        current_low += prob
    return cdf


def arithmetic_encoding(text: str, cdf: Dict[str, Tuple[Decimal, Decimal]]) -> Tuple[Decimal, Decimal]:
    """Encodes the text into a single high-precision real interval [low, high)."""
    low = Decimal('0.0')
    high = Decimal('1.0')

    for char in text:
        current_range = high - low
        char_low, char_high = cdf[char]
        high = low + current_range * char_high
        low = low + current_range * char_low

    return low, high


def fraction_to_binary(low: Decimal, high: Decimal) -> str:
    """Converts the final real interval [low, high) into a binary fraction string."""
    binary_code = "0."
    final_range = high - low
    k = 0
    while (Decimal('2') ** (-k)) > final_range:
        k += 1

    current_val = (low + high) / 2

    for _ in range(k):
        current_val *= 2
        if current_val >= 1:
            binary_code += '1'
            current_val -= 1
        else:
            binary_code += '0'

    return binary_code


def main() -> None:
    text_to_encode = """
Процесор є головним елементом будь-якого комп’ютера чи мобільного пристрою. Він відповідає за виконання всіх арифметичних, логічних і керуючих операцій, необхідних для роботи системи. Сучасні процесори мають багатоядерну архітектуру, що дозволяє одночасно виконувати декілька завдань. Кожне ядро може працювати незалежно, забезпечуючи високу швидкодію при багатозадачності. Важливими характеристиками процесора є тактова частота, кількість ядер, обсяг кеш-пам’яті та енергоспоживання. Висока частота забезпечує швидке виконання інструкцій, однак підвищує тепловиділення. Тому більшість пристроїв мають спеціальні режими енергозбереження, які динамічно регулюють швидкість роботи залежно від навантаження. У мобільних процесорах, таких як MediaTek Helio або Snapdragon, часто поєднуються продуктивні й енергоефективні ядра. Це дозволяє підтримувати баланс між швидкодією та тривалістю роботи від акумулятора. Програмні оптимізації MIUI чи Android також впливають на продуктивність, регулюючи частоти процесора, коли пристрій працює від батареї або підключений до мережі. У майбутньому процесори стануть ще розумнішими — із підтримкою штучного інтелекту, машинного навчання та автоматичної адаптації до поведінки користувача. Вони не лише обчислюватимуть дані, а й прогнозуватимуть потреби системи, забезпечуючи максимальну ефективність при мінімальному енергоспоживанні.
"""

    print(f"Вихідний текст ({len(text_to_encode)} символів):\n{text_to_encode[:200].strip()}...\n")

    processed = preprocess_text(text_to_encode)
    print(f"Текст після обробки ({len(processed)} символів)\n")

    adaptive_probabilities = calculate_frequencies(processed)

    print("--- Адаптивна Модель ---")
    print(f"Знайдено {len(adaptive_probabilities)} унікальних символів.")
    print("Обчислені ймовірності для всіх символів:")

    sorted_probs_list = sorted(adaptive_probabilities.items(), key=lambda item: item[1], reverse=True)
    for char, prob in sorted_probs_list[:10]:
        print(f"  '{char}': {prob:.5f}")
    print("...\n")

    cdf_table = get_cumulative_freqs(adaptive_probabilities)

    print("Кодування, зачекайте кілька секунд...")
    low, high = arithmetic_encoding(processed, cdf_table)

    print(f"low:  {low:.100f}...")
    print(f"high: {high:.100f}...")

    binary_result = fraction_to_binary(low, high)

    print("\n--- РЕЗУЛЬТАТ (Адаптивна модель) ---")
    print(f"Інтервал: [{low:.30f}, {high:.30f})")
    print(f"Довжина: {high - low:.3e}")
    print(f"Двійковий код (перші 200 біт):\n{binary_result[:200]}")


if __name__ == "__main__":
    main()