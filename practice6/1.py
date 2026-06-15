import numpy as np
from typing import Tuple


def generate_matrices_15_11() -> Tuple[np.ndarray, np.ndarray]:
    """
    Generates systematic Generator Matrix G (11x15) and
    Parity-Check Matrix H (4x15) for a Hamming (15, 11) code.
    """
    k = 11  # information bits
    n = 15  # total codeword length
    r = n - k  # parity bits (4)

    # 1. Build parity matrix P: rows are binary digits of numbers that are NOT powers of two
    parity_rows = []
    for i in range(1, n + 1):
        if (i & (i - 1)) != 0:  # If i is not a power of 2
            row = [(i >> bit) & 1 for bit in range(r)]
            parity_rows.append(row)

    P = np.array(parity_rows)  # Matrix P (11x4)
    I_k = np.eye(k, dtype=int)  # Identity matrix I (11x11)

    # Generator matrix G = [I | P]
    G = np.hstack((I_k, P))

    # 2. Build parity-check matrix H = [P^T | I_r]
    P_transposed = P.T  # Transposed P (4x11)
    I_r = np.eye(r, dtype=int)  # Identity matrix I (4x4)

    # Parity check matrix H = [P^T | I]
    H = np.hstack((P_transposed, I_r))

    return G, H


def main() -> None:
    G, H = generate_matrices_15_11()

    print("Породжувальна матриця G:")
    print(G, "\n")
    print("Перевірочна матриця H:")
    print(H)


if __name__ == "__main__":
    main()