import numpy as np

def get_parity_count(n_code, k_data):
    return n_code - k_data


def generate_h_matrix(n, r):
    """
    Генерує перевірочну матрицю H розміром (r x n).
    Стовпці матриці — це бінарні представлення чисел від 1 до n.
    """
    matrix = []
    for row_idx in range(r):
        row = []
        for col_idx in range(1, n + 1):
            # Перевіряємо, чи встановлений біт row_idx у числі col_idx
            # Це формує стовпці: 1 (001), 2 (010), 3 (011) і т.д.
            if (col_idx >> row_idx) & 1:
                row.append(1)
            else:
                row.append(0)
        matrix.append(row)
    return matrix


def hamming_encode(data_str, n, k):
    """
    Кодує вхідний бітовий рядок за кодом Хеммінга (n, k).
    Розставляє контрольні біти на позиціях 1, 2, 4, 8...
    """
    r = get_parity_count(n, k)
    data_bits = [int(b) for b in data_str]

    # 1. Розставляємо інформаційні біти, пропускаючи позиції 1, 2, 4, 8...
    codeword = [0] * n
    data_idx = 0

    for i in range(1, n + 1):
        # Якщо i не є степенем 2 (тобто (i & (i - 1)) != 0), то це місце для даних
        if (i & (i - 1)) != 0:
            if data_idx < len(data_bits):
                codeword[i - 1] = data_bits[data_idx]
                data_idx += 1

    # 2. Обчислюємо біти парності
    for i in range(r):
        pos_parity = 2 ** i
        xor_sum = 0
        for pos in range(1, n + 1):
            # Якщо поточна позиція входить в зону відповідальності цього біта парності
            if pos != pos_parity and (pos & pos_parity):
                xor_sum ^= codeword[pos - 1]
        codeword[pos_parity - 1] = xor_sum

    return codeword


def calculate_syndrome(codeword, H):
    """
    Обчислює синдром S = H * C^T
    """
    r = len(H)
    n = len(H[0])
    syndrome = []

    for i in range(r):
        val = 0
        for j in range(n):
            val ^= (H[i][j] * codeword[j])
        syndrome.append(val)

    return syndrome


def print_matrix(name, matrix):
    print(f"{name}:")
    for row in matrix:
        print("  " + " ".join(str(x) for x in row))


def solve_variant(data_input, n, k):
    print(f"\n{'=' * 10} Код ({n},{k}) | Варіант 2 | Вхід: '{data_input}' {'=' * 10}")

    # 1. Кодування
    codeword = hamming_encode(data_input, n, k)
    codeword_str = "".join(str(x) for x in codeword)
    print(f"Закодоване слово (Codeword): {codeword_str}")

    # 2. Побудова матриці H
    r = n - k
    H = generate_h_matrix(n, r)
    # Виводимо матрицю (можна закоментувати, якщо вона занадто велика для (31,26))
    if n < 20:
        print_matrix("Перевірочна матриця H", H)
    else:
        print("Перевірочна матриця H побудована (занадто велика для виводу в консоль)")

    # 3. Обчислення синдрому (перевірка без помилок)
    syndrome = calculate_syndrome(codeword, H)
    print(f"Синдром (без помилок): {syndrome}")

    # 4. Висновок
    has_error = any(s != 0 for s in syndrome)
    if not has_error:
        print("-> Синдром нульовий. Кодування вірне.")
    else:
        print("-> Синдром не нульовий. Щось пішло не так!")


def solve_with_artificial_error(data_input, n, k, error_pos):
    print(f"\n{'!' * 5} ДЕМОНСТРАЦІЯ ПОМИЛКИ для ({n},{k}) {'!' * 5}")

    # 1. Нормальне кодування
    codeword = hamming_encode(data_input, n, k)

    # 2. Вносимо помилку
    if 1 <= error_pos <= n:
        print(f"Вносимо штучну помилку в біт №{error_pos}...")
        codeword[error_pos - 1] ^= 1  # Інверсія біта
    else:
        print("Невірна позиція помилки!")
        return

    # 3. Обчислення синдрому
    r = n - k
    H = generate_h_matrix(n, r)
    syndrome = calculate_syndrome(codeword, H)

    # Переводимо синдром у десяткове число для зручності
    # (у цьому коді syndrome[0] - це молодший біт)
    syndrome_decimal = 0
    for i, val in enumerate(syndrome):
        syndrome_decimal += val * (2 ** i)

    print(f"Отриманий синдром (bin): {syndrome}")
    print(f"Отриманий синдром (dec): {syndrome_decimal}")

    if syndrome_decimal == error_pos:
        print(f"ВИСНОВОК: Синдром {syndrome_decimal} співпадає з позицією помилки {error_pos}. Код працює!")
    else:
        print("ВИСНОВОК: Синдром не вказує на вірну позицію.")


# --- ЗАПУСК ДЛЯ ВАРІАНТА 2 ---
if __name__ == "__main__":
    # ДАНІ ВАРІАНТУ 2 (Згідно з таблицею)

    # 1. Код (7,4)
    # Інф. послідовність: 1010
    solve_variant("1010", 7, 4)

    # 2. Код (15,11)
    # Інф. послідовність: 11101001100
    solve_variant("11101001100", 15, 11)

    # 3. Код (31,26)
    # Інф. послідовність: 11101001100101000010100011
    solve_variant("11101001100101000010100011", 31, 26)

    # --- ПЕРЕВІРКА СИНДРОМУ (ДЕМОНСТРАЦІЯ) ---
    # Перевіримо на коді (7,4), зіпсувавши 3-й біт
    solve_with_artificial_error("1010", 7, 4, error_pos=3)

    # Перевіримо на коді (15,11), зіпсувавши 7-й біт
    solve_with_artificial_error("11101001100", 15, 11, error_pos=7)