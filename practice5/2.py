import sys
from decimal import Decimal, getcontext
from collections import Counter  # Використаємо Counter для легкого підрахунку

# --- 1. Налаштування ---
getcontext().prec = 2100


# --- 2. Функції для Адаптивної Моделі ---
def preprocess_text(text):
    """Приводимо все до одного регістру."""
    return text.upper()


def calculate_frequencies(text):
    """
    Обчислює точні імовірності для кожного символу в наданому тексті.
    """
    total_chars = Decimal(len(text))
    if total_chars == 0:
        return {}

    counts = Counter(text)

    probabilities = {}
    for char, count in counts.items():
        probabilities[char] = Decimal(count) / total_chars

    return probabilities


# --- 3. Функції, що залишились без змін ---
def get_cumulative_freqs(probabilities):
    """
    Будує кумулятивну таблицю частот (CDF).
    """
    cdf = {}
    current_low = Decimal('0.0')
    # Сортуємо для стабільності
    sorted_probs = sorted(probabilities.items(), key=lambda item: item[0])
    for char, prob in sorted_probs:
        cdf[char] = (current_low, current_low + prob)
        current_low += prob
    return cdf


def arithmetic_encoding(text, cdf):
    """Виконує кодування."""
    low = Decimal('0.0')
    high = Decimal('1.0')

    for i, char in enumerate(text):
        current_range = high - low
        char_low, char_high = cdf[char]
        high = low + current_range * char_high
        low = low + current_range * char_low

    return low, high


def fraction_to_binary(low, high):
    """Конвертує інтервал у двійковий код."""
    binary_code = "0."
    final_range = high - low
    max_bits = 200
    k = 0
    #and k < max_bits
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


# --- 4. Запуск ---
text_to_encode = """
Процесор є головним елементом будь-якого комп’ютера чи мобільного пристрою. Він відповідає за виконання всіх арифметичних, логічних і керуючих операцій, необхідних для роботи системи. Сучасні процесори мають багатоядерну архітектуру, що дозволяє одночасно виконувати декілька завдань. Кожне ядро може працювати незалежно, забезпечуючи високу швидкодію при багатозадачності. Важливими характеристиками процесора є тактова частота, кількість ядер, обсяг кеш-пам’яті та енергоспоживання. Висока частота забезпечує швидке виконання інструкцій, однак підвищує тепловиділення. Тому більшість пристроїв мають спеціальні режими енергозбереження, які динамічно регулюють швидкість роботи залежно від навантаження. У мобільних процесорах, таких як MediaTek Helio або Snapdragon, часто поєднуються продуктивні й енергоефективні ядра. Це дозволяє підтримувати баланс між швидкодією та тривалістю роботи від акумулятора. Програмні оптимізації MIUI чи Android також впливають на продуктивність, регулюючи частоти процесора, коли пристрій працює від батареї або підключений до мережі. У майбутньому процесори стануть ще розумнішими — із підтримкою штучного інтелекту, машинного навчання та автоматичної адаптації до поведінки користувача. Вони не лише обчислюватимуть дані, а й прогнозуватимуть потреби системи, забезпечуючи максимальну ефективність при мінімальному енергоспоживанні.
"""

print(f"Вихідний текст ({len(text_to_encode)} символів):\n{text_to_encode[:200]}...\n")

# 1. Готуємо текст (тільки .upper())
processed = preprocess_text(text_to_encode)
print(f"Текст після обробки ({len(processed)} символів)\n")

# 2. Обчислюємо імовірності з тексту
adaptive_probabilities = calculate_frequencies(processed)

print(f"--- Адаптивна Модель ---")
print(f"Знайдено {len(adaptive_probabilities)} унікальних символів.")
print("Обчислені імовірності для всіх символів:")

# Сортуємо для зручності читання
sorted_probs_list = sorted(adaptive_probabilities.items(), key=lambda item: item[1], reverse=True)

for char, prob in sorted_probs_list:
    print(f"  '{char}': {prob:.5f}")  # {prob} - це і є імовірність
print("...\n")

# 3. Будуємо CDF на основі цих імовірностей
cdf_table = get_cumulative_freqs(adaptive_probabilities)

# 4. Кодуємо
print("Кодування, зачекайте кілька секунд...")
low, high = arithmetic_encoding(processed, cdf_table)

print(low)
print(high)

binary_result = fraction_to_binary(low, high)

print("\n--- РЕЗУЛЬТАТ (Адаптивна модель) ---")
print(f"Інтервал: [{low:.30f}, {high:.30f})")
print(f"Довжина: {high - low:.3e}")
print(f"Двійковий код (200 біт максимум):\n{binary_result}")