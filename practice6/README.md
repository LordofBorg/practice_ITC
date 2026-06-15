# Practice 6: Hamming Error-Correcting Codes

## Objective
The objective of this practice is to design, implement, and analyze linear block error-correcting codes, specifically **Hamming codes** in the formats (7,4), (15,11), and (31,26). The project implements code generators, parity calculators, syndrome analyzers, and automatic single-bit error correction systems.

---

## Mathematical Model

1. **Parameters**:
   * $n$: Total codeword length.
   * $k$: Information (data) bits.
   * $r = n - k$: Parity (check) bits.
   * Check bits must satisfy the **Hamming Inequality**:
     $$2^r \ge k + r + 1 \quad \text{or} \quad 2^r \ge n + 1$$

2. **Systematic Generator Matrix $G$**:
   A $k \times n$ matrix used to encode the information word $D$ (length $k$) into systematic codeword $C = D \cdot G$:
   $$G = [I_k \mid P]$$
   where $I_k$ is the $k \times k$ identity matrix, and $P$ is a $k \times r$ parity-check matrix.

3. **Systematic Parity-Check Matrix $H$**:
   An $r \times n$ matrix used to verify the integrity of the received codeword:
   $$H = [P^T \mid I_r]$$
   where $P^T$ is the transpose of $P$, and $I_r$ is the $r \times r$ identity matrix.

4. **Classical Parity Placement & Matrix $H$**:
   In classical Hamming codes (often used in hardware), parity bits are placed at power-of-2 positions ($1, 2, 4, 8, \dots$). The columns of the $H$ matrix correspond directly to the binary representation of column indexes from $1$ to $n$:
   $$H = [h_1, h_2, \dots, h_n]$$
   where $h_j$ is the binary representation of the index $j$ (e.g., column 3 is $011^T$).

5. **Syndrome Calculation & Error Correction**:
   For a received codeword vector $X$, the syndrome vector $S$ (length $r$) is calculated as:
   $$S = X \cdot H^T \pmod 2$$
   * If $S = 0$, the message was transmitted without errors.
   * If $S \neq 0$, under classical indexing, the decimal value of the binary vector $S$ represents the **1-based index** of the corrupted bit.
   * Correction is performed by inverting the corrupted bit:
     $$X_{\text{corrected}}[S - 1] = X[S - 1] \oplus 1$$

---

## Codebase Structure & Components

* **[1.py](1.py)**: Matrix generation script. Constructs systematic matrices $G$ and $H$ for the (15,11) Hamming code by selecting rows of $P$ that correspond to numbers which are not powers of two.
* **[2.py](2.py)**: Full Hamming coder/decoder simulator. Implements:
  * Check bit calculations for power-of-2 locations.
  * Classical $H$ matrix generation.
  * Hamming (7,4), (15,11), and (31,26) testing.
  * Artificial error injection to verify the syndrome-based correction mechanism.

---

## Performance & Verification

Running `2.py` demonstrates the encoding and decoding flows:

* **No-Error Flow**:
  1. Input data `1010` (length 4) is encoded to `1010010` (length 7, using power-of-2 parity locations).
  2. Syndrome is computed: $S = [0, 0, 0]$. Since $S=0$, the word is valid.
* **Error Correction Flow**:
  1. Input data `11101001100` (length 11) is encoded into a 15-bit codeword.
  2. Artificial error is introduced in bit position **7**.
  3. The syndrome is calculated: $S = [1, 1, 1, 0]$ (in binary, little-endian).
  4. Converting $S$ to decimal: $1 \cdot 2^0 + 1 \cdot 2^1 + 1 \cdot 2^2 + 0 \cdot 2^3 = 7$.
  5. The decoder identifies that the error is in bit 7, flips it, and recovers the original message.

---

## How to Run

1. Generate (15, 11) systematic matrices:
   ```bash
   python 1.py
   ```
2. Simulate error injection and correction:
   ```bash
   python 2.py
   ```
