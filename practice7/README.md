# Practice 7: Systematic Cyclic Codes (CRC)

## Objective
The objective of this practice is to implement systematic cyclic codes based on polynomial arithmetic over Galois Field $GF(2)$ to perform **Cyclic Redundancy Checks (CRC)**. The project models systematic polynomial encoding (remainder calculation) and syndrome-based error detection.

---

## Mathematical Model

1. **Galois Field $GF(2)$ Arithmetic**:
   All coefficients of the message and generator polynomials belong to the set $\{0, 1\}$. Addition and subtraction operations are mathematically equivalent to the bitwise **XOR** operation:
   $$1 \oplus 1 = 0, \quad 1 \oplus 0 = 1, \dots$$
   There are no carries or borrows.

2. **Systematic Encoding**:
   * Let the input message be represented by the polynomial $G(x)$.
   * Let the generator polynomial be $P(x)$ of degree $r$ (length $r + 1$).
   * Multiply the message polynomial by $x^r$ (conceptually shifting it to the left by $r$ bits, padding the tail with $r$ zeros):
     $$T_{\text{padded}}(x) = G(x) \cdot x^r$$
   * Perform modulo-2 division of $T_{\text{padded}}(x)$ by $P(x)$ to obtain the remainder polynomial $R(x)$ (degree $< r$):
     $$R(x) = \left(G(x) \cdot x^r\right) \pmod{P(x)}$$
   * The systematic codeword $F(x)$ is formed by replacing the padded zeros with the remainder bits:
     $$F(x) = G(x) \cdot x^r \oplus R(x)$$

3. **Error Detection (Syndrome Decoding)**:
   * The receiver divides the received codeword $F'(x)$ by the generator polynomial $P(x)$.
   * The remainder of this division represents the syndrome $S(x)$:
     $$S(x) = F'(x) \pmod{P(x)}$$
   * If $S(x) = 0$, the transmission is assumed error-free.
   * If $S(x) \neq 0$, an error is successfully detected.

---

## Codebase Structure & Components

* **[1.py](1.py)**: Python script implementing polynomial CRC logic:
  * `CRCCoder`: Class initialized with a generator polynomial (e.g., `'1011'` representing $x^3 + x + 1$).
  * `_mod2_div`: Performs bit-by-bit modulo-2 division using sliding window XOR operations.
  * `encode`: Systematic CRC encoder.
  * `check_errors`: Calculates the remainder (syndrome) and checks if it contains non-zero bits.
  * Runs validations for (7,4) and (15,11) formats.

---

## Verification & Execution Flow

* **Hamming-style (7,4) Cyclic Code**:
  * Input Message: `1010`
  * Generator Polynomial: `1011` ($x^3 + x + 1$, degree $r=3$)
  * Padded Message: `1010000`
  * Modulo-2 Division: `1010000` / `1011` yields remainder `011`.
  * Codeword: `1010011`
  * Integrity Check:
    * Uncorrupted codeword `1010011` $\rightarrow$ Syndrome `000` (OK).
    * Corrupted codeword (bit 2 flipped) `1000011` $\rightarrow$ Syndrome `010` (ERROR detected).

* **(15,11) Cyclic Code**:
  * Input Message: `11101001100`
  * Generator Polynomial: `10011` ($x^4 + x + 1$, degree $r=4$)
  * Codeword: `111010011000100`
  * Integrity Check:
    * Uncorrupted codeword $\rightarrow$ Syndrome `0000` (OK).
    * Corrupted codeword (bit 5 flipped) $\rightarrow$ Syndrome `0111` (ERROR detected).

---

## How to Run

1. Run the CRC validator:
   ```bash
   python 1.py
   ```
