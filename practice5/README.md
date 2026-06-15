# Practice 5: Huffman Block Coding & Arithmetic Coding

## Objective
The objective of this practice is to implement and analyze two optimal source compression algorithms:
1. **Huffman Block Coding**: Group symbols into blocks of length $L$ ($L=1..4$) to approach the theoretical compression limit defined by Shannon's First Theorem.
2. **Arithmetic Coding**: Map entire messages into a single, high-precision floating-point interval, demonstrating a close-to-optimal compression technique for large text structures.

---

## Mathematical Model

### 1. Huffman Block Coding
* **Block Probabilities**:
  For an alphabet with two independent symbols $x_1$ ($p_1 = 0.82$) and $x_2$ ($p_2 = 0.18$), the probability of a block $S_k = (s_1 s_2 \dots s_L)$ is:
  $$P(S_k) = \prod_{j=1}^{L} P(s_j)$$
  There are $2^L$ possible block combinations.
* **Huffman Tree**:
  Sort blocks by probability, recursively combine the two least probable nodes, assign bits `0` and `1`, and read the prefix codes.
* **Average Lengths**:
  * Average code length per block (in bits/block):
    $$\bar{n} = \sum_{k=1}^{2^L} P(S_k) l_k$$
  * Average code length per symbol (in bits/symbol):
    $$\bar{n}_c = \frac{\bar{n}}{L}$$
* **Source & Code Redundancy**:
  * Source Redundancy (under-utilization due to probability skew):
    $$\chi_d = 1 - \frac{H(X)}{\log_2(2)} = 1 - H(X)$$
  * Code Redundancy (unused compression potential in the code):
    $$\chi_k = 1 - \frac{H(S)}{\bar{n}} = 1 - \frac{L \cdot H(X)}{\bar{n}}$$

### 2. Arithmetic Coding
* **Principles**:
  Unlike Huffman, which assigns an integer number of bits to each symbol/block, Arithmetic coding represents the entire text by a single real number in the range $[0, 1)$.
* **Interval Narrowing**:
  Given a character cumulative distribution function (CDF) range $[CDF_{low}(c), CDF_{high}(c))$, the global interval $[low, high)$ (initially $[0, 1)$) narrows for each character $c$ in the message:
  $$\text{range} = \text{high} - \text{low}$$
  $$\text{high} = \text{low} + \text{range} \cdot CDF_{high}(c)$$
  $$\text{low} = \text{low} + \text{range} \cdot CDF_{low}(c)$$
* **Arbitrary Precision Arithmetic**:
  As text length grows, the interval shrinks exponentially. To prevent underflow, we use the `decimal` library with **2100 decimal digits** of precision.

---

## Codebase Structure & Components

* **[1.py](1.py)**: Generates blocks for $L=1..4$, constructs Huffman trees, outputs tabular results, and plots dependencies:
  * Entropy vs. block length $L$.
  * Average code lengths.
  * Redundancy metrics.
* **[2.py](2.py)**: Performs adaptive Arithmetic coding. It takes a custom Ukrainian text, calculates exact frequencies, builds a CDF, processes the characters to obtain the final arbitrary-precision binary fraction, and prints the result.

---

## Huffman Block Coding Performance Results

Running the block encoder on base probabilities $P(x_1) = 0.82$, $P(x_2) = 0.18$ yields the following results:

### Huffman Codebooks for different block lengths $L$:

* **$L=1$ (No blocking)**:
  * `x1` ($p=0.82$) $\rightarrow$ `1` (length 1)
  * `x2` ($p=0.18$) $\rightarrow$ `0` (length 1)
* **$L=2$**:
  * `x1·x1` ($p=0.6724$) $\rightarrow$ `1` (length 1)
  * `x2·x1` ($p=0.1476$) $\rightarrow$ `00` (length 2)
  * `x1·x2` ($p=0.1476$) $\rightarrow$ `011` (length 3)
  * `x2·x2` ($p=0.0324$) $\rightarrow$ `010` (length 3)
* **$L=3$**:
  * `x1·x1·x1` ($p=0.5514$) $\rightarrow$ `1` (length 1)
  * `x1·x2·x1` ($p=0.1210$) $\rightarrow$ `010` (length 3)
  * `x2·x1·x1` ($p=0.1210$) $\rightarrow$ `011` (length 3)
  * `x1·x1·x2` ($p=0.1210$) $\rightarrow$ `001` (length 3)
  * ... (lower probability blocks get codes of length 5)
* **$L=4$**:
  * `x1·x1·x1·x1` ($p=0.4521$) $\rightarrow$ `0` (length 1)
  * ... (lower probability blocks get codes up to length 9)

### Tabular Performance Summary:

| Block Length $L$ | Block Entropy $H(S)$ [bits] | Minimum Length $n_{\text{min}}$ | Avg Block Length $\bar{n}$ [bits] | Avg Symbol Length $\bar{n}_c$ [bits/sym] | Source Redundancy $\chi_d$ | Code Redundancy $\chi_k$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 0.68008 | 1 | 1.00000 | 1.00000 | 0.31992 | 0.31992 (32.0%) |
| **2** | 1.36015 | 1 | 1.50760 | 0.75380 | 0.31992 | 0.09780 (9.78%) |
| **3** | 2.04023 | 1 | 2.06834 | 0.68945 | 0.31992 | 0.01359 (1.36%) |
| **4** | 2.72031 | 1 | 2.77133 | 0.69283 | 0.31992 | 0.01841 (1.84%) |

*Analysis*: The source redundancy remains constant ($\approx 32\%$) because the underlying source distribution does not change. However, by coding symbols in blocks, the code redundancy $\chi_k$ drops from **$32\%$** for unblocked coding down to **$1.36\%$** for $L=3$, bringing the average symbol code length $\bar{n}_c \approx 0.689$ bits/sym extremely close to the source entropy $H(X) \approx 0.680$ bits/sym.

---

## How to Run

1. Run Huffman simulation (generates summary tables and saves 3 matplotlib charts in memory/GUI):
   ```bash
   python 1.py
   ```
2. Run Arithmetic coding simulation on Ukrainian text:
   ```bash
   python 2.py
   ```
