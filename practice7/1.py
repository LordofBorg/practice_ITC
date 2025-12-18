import numpy as np


class CRCCoder:
    def __init__(self, generator_poly_str):
        """
        Ініціалізація кодера породжуючим поліномом.
        Вхід: рядок бітів, наприклад '1011' для x^3 + x + 1.
        """
        # Перетворюємо рядок у список цілих чисел для зручної роботи
        self.generator = [int(b) for b in generator_poly_str]
        # Степінь полінома (r) дорівнює довжині мінус 1
        self.r = len(self.generator) - 1

    def _mod2_div(self, dividend_bits):
        """
        Виконує ділення поліномів за модулем 2 (операція XOR).
        Повертає остачу (R(x)).
        """
        # Робимо копію, щоб не змінювати оригінал
        bits = dividend_bits.copy()

        # Проходимо по бітах. Ділення йде доти, поки довжина залишку >= дільника
        len_gen = len(self.generator)
        len_bits = len(bits)

        for i in range(len_bits - len_gen + 1):
            # Якщо старший біт дорівнює 1, виконуємо XOR з дільником
            if bits[i] == 1:
                for j in range(len_gen):
                    bits[i + j] ^= self.generator[j]

        # Остача - це останні r бітів після завершення циклу
        # (Оскільки старші біти обнулилися)
        remainder = bits[-(len_gen - 1):]
        return remainder

    def encode(self, info_bits_str):
        """
        Кодування систематичним циклічним кодом.
        1. Зсув вліво на r (додавання нулів).
        2. Обчислення остачі.
        3. Формування кодового слова.
        """
        info_bits = [int(b) for b in info_bits_str]

        # Крок 1: Множення на x^r (додавання r нулів в кінець)
        padded_msg = info_bits + [0] * self.r

        # Крок 2: Обчислення залишку R(x) = (G(x) * x^r) mod P(x)
        remainder = self._mod2_div(padded_msg)

        # Крок 3: Формування кодового слова F(x) = (G(x) * x^r) + R(x)
        # У двійковій арифметиці додавання залишку - це просто заміна нулів у хвості
        codeword = info_bits + remainder

        return {
            "input": info_bits_str,
            "padded": "".join(map(str, padded_msg)),
            "remainder": "".join(map(str, remainder)),
            "codeword": "".join(map(str, codeword))
        }

    def check_errors(self, received_codeword_str):
        """
        Перевірка на наявність помилок (синдромне декодування).
        Якщо остача від ділення на P(x) дорівнює 0, помилок немає.
        """
        received_bits = [int(b) for b in received_codeword_str]
        remainder = self._mod2_div(received_bits)

        # Перевіряємо, чи є хоча б одна одиниця в залишку
        has_error = any(bit == 1 for bit in remainder)
        syndrome = "".join(map(str, remainder))

        return not has_error, syndrome


# --- ВИКОНАННЯ ЗАВДАННЯ (Варіант 1) ---

print("=== ЗАВДАННЯ 1: Код (7,4) ===")
# З таблиці: Варіант 1, Інформаційна послідовність (7,4): 1011
# Породжуючий поліном для (7,4) обираємо з таблиці.
# Класичний приклад: x^3 + x + 1 -> 1011
msg_7_4 = "1010"
poly_7_4 = "1011"

coder1 = CRCCoder(poly_7_4)
result1 = coder1.encode(msg_7_4)

print(f"Інформація: {result1['input']}")
print(f"Породжуючий поліном: {poly_7_4}")
print(f"Зсунута послідовність (x^r): {result1['padded']}")
print(f"Остача (R): {result1['remainder']}")
print(f"Кодове слово (Systematic): {result1['codeword']}")

# Перевірка декодера
is_valid, synd = coder1.check_errors(result1['codeword'])
print(f"Перевірка коректного слова: {'OK' if is_valid else 'ERROR'} (Синдром: {synd})")

# Вносимо помилку
corrupted_7_4 = list(result1['codeword'])
corrupted_7_4[2] = '0' if corrupted_7_4[2] == '1' else '1'  # Інвертуємо біт
corrupted_7_4 = "".join(corrupted_7_4)
is_valid_err, synd_err = coder1.check_errors(corrupted_7_4)
print(f"Перевірка слова з помилкою ({corrupted_7_4}): {'OK' if is_valid_err else 'ERROR'} (Синдром: {synd_err})")

print("\n=== ЗАВДАННЯ 2: Код (15,11) ===")
# З таблиці: Варіант 1, Інформаційна послідовність (15,11): 10011001110
# Для коду (15,11) r = 15-11 = 4.
# Обираємо поліном ступеня 4 з таблиці.
# Наприклад, P1(x^4) = x^4 + x + 1 -> 10011
msg_15_11 = "11101001100"
poly_15_11 = "10011"

coder2 = CRCCoder(poly_15_11)
result2 = coder2.encode(msg_15_11)

print(f"Інформація: {result2['input']}")
print(f"Породжуючий поліном: {poly_15_11}")
print(f"Зсунута послідовність (x^r): {result2['padded']}")
print(f"Остача (R): {result2['remainder']}")
print(f"Кодове слово (Systematic): {result2['codeword']}")

# Перевірка декодера
is_valid2, synd2 = coder2.check_errors(result2['codeword'])
print(f"Перевірка коректного слова: {'OK' if is_valid2 else 'ERROR'} (Синдром: {synd2})")

# Вносимо помилку
corrupted_15_11 = list(result2['codeword'])
corrupted_15_11[5] = '0' if corrupted_15_11[5] == '1' else '1'  # Інвертуємо біт
corrupted_15_11 = "".join(corrupted_15_11)
is_valid_err2, synd_err2 = coder2.check_errors(corrupted_15_11)
print(f"Перевірка слова з помилкою ({corrupted_15_11}): {'OK' if is_valid_err2 else 'ERROR'} (Синдром: {synd_err2})")