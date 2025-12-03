import numpy as np


def generate_matrices_15_11():
    k = 11  # інформаційні біти
    n = 15  # загальна довжина
    r = n - k  # перевірочні біти (4)

    # 1. ГЕНЕРАЦІЯ G (як у минулому кроці)
    # Створюємо частину P: рядки - це числа, що не є ступенем двійки
    parity_rows = []
    for i in range(1, n + 1):
        if (i & (i - 1)) != 0:  # Якщо число НЕ ступінь 2
            # Перетворення числа в біти (Little Endian для узгодження)
            row = [(i >> bit) & 1 for bit in range(r)]
            parity_rows.append(row)

    P = np.array(parity_rows)  # Матриця P (11x4)
    I_k = np.eye(k, dtype=int)  # Матриця I (11x11)

    # Породжуюча матриця G = [I | P]
    G = np.hstack((I_k, P))

    # 2. ПОБУДОВА H
    # Формула: H = [P_transposed | I_r]

    P_transposed = P.T  # Транспонуємо P (стає 4x11)
    I_r = np.eye(r, dtype=int)  # Одинична матриця для H (4x4)

    # Об'єднуємо: спочатку P^T, потім I_r
    H = np.hstack((P_transposed, I_r))

    return G, H


# Виклик функції
G, H = generate_matrices_15_11()

print("Породжувача матриця g:")
print(G, "\n")
print("Перевірочна матриця H:")
print(H)