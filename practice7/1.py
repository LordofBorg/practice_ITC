from typing import List, Dict, Tuple


class CRCCoder:
    def __init__(self, generator_poly_str: str) -> None:
        """
        Initializes the CRC coder with a generator polynomial binary string.
        Example: '1011' for x^3 + x + 1.
        """
        self.generator = [int(b) for b in generator_poly_str]
        self.r = len(self.generator) - 1

    def _mod2_div(self, dividend_bits: List[int]) -> List[int]:
        """
        Performs polynomial division modulo 2 using XOR operations.
        Returns the remainder polynomial R(x) (represented as a bit list).
        """
        bits = dividend_bits.copy()
        len_gen = len(self.generator)
        len_bits = len(bits)

        for i in range(len_bits - len_gen + 1):
            if bits[i] == 1:
                for j in range(len_gen):
                    bits[i + j] ^= self.generator[j]

        # The remainder consists of the last r bits
        remainder = bits[-(len_gen - 1):]
        return remainder

    def encode(self, info_bits_str: str) -> Dict[str, str]:
        """
        Encodes the input bit string into a systematic cyclic code (CRC).
        Appends the calculated remainder polynomial to the message.
        """
        info_bits = [int(b) for b in info_bits_str]

        # 1. Multiply by x^r (pad with r zeros)
        padded_msg = info_bits + [0] * self.r

        # 2. Divide modulo 2 to find remainder R(x)
        remainder = self._mod2_div(padded_msg)

        # 3. Form codeword F(x) = message + remainder
        codeword = info_bits + remainder

        return {
            "input": info_bits_str,
            "padded": "".join(map(str, padded_msg)),
            "remainder": "".join(map(str, remainder)),
            "codeword": "".join(map(str, codeword))
        }

    def check_errors(self, received_codeword_str: str) -> Tuple[bool, str]:
        """
        Performs syndrome-based error check on the received codeword string.
        Returns True if syndrome is all-zero (no errors), along with the syndrome string.
        """
        received_bits = [int(b) for b in received_codeword_str]
        remainder = self._mod2_div(received_bits)

        has_error = any(bit == 1 for bit in remainder)
        syndrome = "".join(map(str, remainder))

        return not has_error, syndrome


def main() -> None:
    # -----------------------------
    # TASK 1: Hamming-style (7,4) Cyclic Code
    # -----------------------------
    print("=== ЗАВДАННЯ 1: Код (7,4) ===")
    msg_7_4 = "1010"
    poly_7_4 = "1011"  # x^3 + x + 1

    coder1 = CRCCoder(poly_7_4)
    result1 = coder1.encode(msg_7_4)

    print(f"Інформація: {result1['input']}")
    print(f"Породжуючий поліном: {poly_7_4}")
    print(f"Зсунута послідовність (x^r): {result1['padded']}")
    print(f"Остача (R): {result1['remainder']}")
    print(f"Кодове слово (Systematic): {result1['codeword']}")

    is_valid, synd = coder1.check_errors(result1['codeword'])
    print(f"Перевірка коректного слова: {'OK' if is_valid else 'ERROR'} (Синдром: {synd})")

    # Inject bit error
    corrupted_7_4 = list(result1['codeword'])
    corrupted_7_4[2] = '0' if corrupted_7_4[2] == '1' else '1'
    corrupted_7_4_str = "".join(corrupted_7_4)
    is_valid_err, synd_err = coder1.check_errors(corrupted_7_4_str)
    print(f"Перевірка слова з помилкою ({corrupted_7_4_str}): {'OK' if is_valid_err else 'ERROR'} (Синдром: {synd_err})")

    # -----------------------------
    # TASK 2: (15,11) Cyclic Code
    # -----------------------------
    print("\n=== ЗАВДАННЯ 2: Код (15,11) ===")
    msg_15_11 = "11101001100"
    poly_15_11 = "10011"  # x^4 + x + 1

    coder2 = CRCCoder(poly_15_11)
    result2 = coder2.encode(msg_15_11)

    print(f"Інформація: {result2['input']}")
    print(f"Породжуючий поліном: {poly_15_11}")
    print(f"Зсунута послідовність (x^r): {result2['padded']}")
    print(f"Остача (R): {result2['remainder']}")
    print(f"Кодове слово (Systematic): {result2['codeword']}")

    is_valid2, synd2 = coder2.check_errors(result2['codeword'])
    print(f"Перевірка коректного слова: {'OK' if is_valid2 else 'ERROR'} (Синдром: {synd2})")

    # Inject bit error
    corrupted_15_11 = list(result2['codeword'])
    corrupted_15_11[5] = '0' if corrupted_15_11[5] == '1' else '1'
    corrupted_15_11_str = "".join(corrupted_15_11)
    is_valid_err2, synd_err2 = coder2.check_errors(corrupted_15_11_str)
    print(f"Перевірка слова з помилкою ({corrupted_15_11_str}): {'OK' if is_valid_err2 else 'ERROR'} (Синдром: {synd_err2})")


if __name__ == "__main__":
    main()