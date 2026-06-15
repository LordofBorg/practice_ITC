from typing import List


def get_parity_count(n_code: int, k_data: int) -> int:
    """Returns the number of parity bits required for (n, k) code."""
    return n_code - k_data


def generate_h_matrix(n: int, r: int) -> List[List[int]]:
    """
    Generates classical Hamming parity-check matrix H of size r x n.
    Columns are binary representations of column indices 1 to n.
    """
    matrix = []
    for row_idx in range(r):
        row = []
        for col_idx in range(1, n + 1):
            if (col_idx >> row_idx) & 1:
                row.append(1)
            else:
                row.append(0)
        matrix.append(row)
    return matrix


def hamming_encode(data_str: str, n: int, k: int) -> List[int]:
    """
    Encodes the given input bit string into a Hamming (n, k) codeword.
    Parity check bits are placed at positions that are powers of 2.
    """
    r = get_parity_count(n, k)
    data_bits = [int(b) for b in data_str]

    # Initialize codeword with zeros
    codeword = [0] * n
    data_idx = 0

    # 1. Place data bits in locations that are NOT powers of 2
    for i in range(1, n + 1):
        if (i & (i - 1)) != 0:  # If i is not a power of 2
            if data_idx < len(data_bits):
                codeword[i - 1] = data_bits[data_idx]
                data_idx += 1

    # 2. Compute parity check bits
    for i in range(r):
        pos_parity = 2 ** i
        xor_sum = 0
        for pos in range(1, n + 1):
            if pos != pos_parity and (pos & pos_parity):
                xor_sum ^= codeword[pos - 1]
        codeword[pos_parity - 1] = xor_sum

    return codeword


def calculate_syndrome(codeword: List[int], H: List[List[int]]) -> List[int]:
    """Computes the syndrome vector S = H * C^T modulo 2."""
    r = len(H)
    n = len(H[0])
    syndrome = []

    for i in range(r):
        val = 0
        for j in range(n):
            val ^= (H[i][j] * codeword[j])
        syndrome.append(val)

    return syndrome


def print_matrix(name: str, matrix: List[List[int]]) -> None:
    """Prints a 2D matrix formatted with spaces."""
    print(f"{name}:")
    for row in matrix:
        print("  " + " ".join(str(x) for x in row))


def solve_variant(data_input: str, n: int, k: int) -> None:
    """Simulates Hamming encoding, matrix generation, and verification on input data."""
    print(f"\n{'=' * 10} Код ({n},{k}) | Вхід: '{data_input}' {'=' * 10}")

    # 1. Hamming Encode
    codeword = hamming_encode(data_input, n, k)
    codeword_str = "".join(str(x) for x in codeword)
    print(f"Закодоване слово (Codeword): {codeword_str}")

    # 2. Generate H matrix
    r = n - k
    H = generate_h_matrix(n, r)
    if n < 20:
        print_matrix("Перевірочна матриця H", H)
    else:
        print("Перевірочна матриця H побудована (занадто велика для консолі)")

    # 3. Calculate syndrome (expected to be zero for clean transmission)
    syndrome = calculate_syndrome(codeword, H)
    print(f"Синдром (без помилок): {syndrome}")

    has_error = any(s != 0 for s in syndrome)
    if not has_error:
        print("-> Синдром нульовий. Кодування вірне.")
    else:
        print("-> Синдром не нульовий. Щось пішло не так!")


def solve_with_artificial_error(data_input: str, n: int, k: int, error_pos: int) -> None:
    """Encodes input data, injects a single bit error, and verifies syndrome localization."""
    print(f"\n{'!' * 5} ДЕМОНСТРАЦІЯ ПОМИЛКИ для ({n},{k}) {'!' * 5}")

    # 1. Normal coding
    codeword = hamming_encode(data_input, n, k)

    # 2. Inject bit corruption
    if 1 <= error_pos <= n:
        print(f"Вносимо штучну помилку в біт №{error_pos}...")
        codeword[error_pos - 1] ^= 1  # Invert bit
    else:
        print("Невірна позиція помилки!")
        return

    # 3. Calculate syndrome
    r = n - k
    H = generate_h_matrix(n, r)
    syndrome = calculate_syndrome(codeword, H)

    # Convert binary syndrome vector to decimal index
    syndrome_decimal = sum(val * (2 ** i) for i, val in enumerate(syndrome))

    print(f"Отриманий синдром (bin): {syndrome}")
    print(f"Отриманий синдром (dec): {syndrome_decimal}")

    if syndrome_decimal == error_pos:
        print(f"ВИСНОВОК: Синдром {syndrome_decimal} співпадає з позицією помилки {error_pos}. Код працює!")
    else:
        print("ВИСНОВОК: Синдром не вказує на вірну позицію.")


def main() -> None:
    # Test cases:
    # 1. Code (7,4)
    solve_variant("1010", 7, 4)

    # 2. Code (15,11)
    solve_variant("11101001100", 15, 11)

    # 3. Code (31,26)
    solve_variant("11101001100101000010100011", 31, 26)

    # Error localization demonstration
    solve_with_artificial_error("1010", 7, 4, error_pos=3)
    solve_with_artificial_error("11101001100", 15, 11, error_pos=7)


if __name__ == "__main__":
    main()