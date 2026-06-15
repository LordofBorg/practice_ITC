"""
Computes entropy metrics H(A), H(B), H(A,B), H(B|A), H(A|B)
for a given joint probability matrix P(A,B).
"""
import numpy as np
from typing import Tuple, List, Optional

# Formatting array output: 6 decimal places, no scientific notation
np.set_printoptions(precision=6, suppress=True)

# Small value to avoid log(0)
EPS = 1e-12


def normalize_matrix(mat: np.ndarray) -> np.ndarray:
    """Normalizes the matrix so that the sum of all elements equals 1."""
    s = np.sum(mat)
    if s <= 0:
        raise ValueError("Matrix elements sum must be greater than zero.")
    return mat / s


def marginal_from_joint(joint: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Calculates marginal probabilities P(A) (row sums) and P(B) (column sums)."""
    pA = np.sum(joint, axis=1)
    pB = np.sum(joint, axis=0)
    return pA, pB


def conditional_A_given_B(joint: np.ndarray, pB: np.ndarray) -> np.ndarray:
    """Calculates the conditional probabilities matrix P(A|B)."""
    cond = np.zeros_like(joint)
    for b in range(joint.shape[1]):
        if pB[b] > 0:
            cond[:, b] = joint[:, b] / pB[b]
        else:
            cond[:, b] = 0.0
    return cond


def conditional_B_given_A(joint: np.ndarray, pA: np.ndarray) -> np.ndarray:
    """Calculates the conditional probabilities matrix P(B|A)."""
    cond = np.zeros_like(joint)
    for a in range(joint.shape[0]):
        if pA[a] > 0:
            cond[a, :] = joint[a, :] / pA[a]
        else:
            cond[a, :] = 0.0
    return cond


def entropy_of_distribution(p: np.ndarray) -> float:
    """Computes Shannon entropy H(X) for a 1D probability distribution in bits."""
    p_arr = np.asarray(p, dtype=float)
    p_nonzero = p_arr[p_arr > EPS]
    return float(-np.sum(p_nonzero * np.log2(p_nonzero)))


def joint_entropy(joint: np.ndarray) -> float:
    """Computes joint entropy H(A,B) in bits."""
    flat = joint.flatten()
    flat_nz = flat[flat > EPS]
    return float(-np.sum(flat_nz * np.log2(flat_nz)))


def conditional_entropy_A_given_B(joint: np.ndarray, pB: np.ndarray) -> float:
    """Computes conditional entropy H(A|B) = sum_b P(b) * H(A|B=b) in bits."""
    H = 0.0
    for b in range(joint.shape[1]):
        pb = pB[b]
        if pb > EPS:
            pA_given_b = joint[:, b] / pb
            H_ab = entropy_of_distribution(pA_given_b)
            H += pb * H_ab
    return float(H)


def conditional_entropy_B_given_A(joint: np.ndarray, pA: np.ndarray) -> float:
    """Computes conditional entropy H(B|A) = sum_a P(a) * H(B|A=a) in bits."""
    H = 0.0
    for a in range(joint.shape[0]):
        pa = pA[a]
        if pa > EPS:
            pB_given_a = joint[a, :] / pa
            H_ba = entropy_of_distribution(pB_given_a)
            H += pa * H_ba
    return float(H)


def pretty_print_matrix(
    mat: np.ndarray,
    row_labels: Optional[List[str]] = None,
    col_labels: Optional[List[str]] = None,
    title: Optional[str] = None
) -> None:
    """Prints a matrix with labeled columns and rows."""
    if title:
        print(title)
    rows, cols = mat.shape
    if col_labels is None:
        col_labels = [f"B{j}" for j in range(cols)]
    if row_labels is None:
        row_labels = [f"A{i}" for i in range(rows)]
    header = "      " + " ".join(f"{c:>9}" for c in col_labels)
    print(header)
    for i in range(rows):
        row_str = f"{row_labels[i]:>4}  " + " ".join(f"{mat[i,j]:9.6f}" for j in range(cols))
        print(row_str)
    print()


def main() -> None:
    # Set seed for reproducibility
    np.random.seed(1337)

    # Variant 2: Random 9x9 probability matrix
    rand = np.random.rand(9, 9)
    joint = normalize_matrix(rand)

    # Derive marginals and conditionals
    pA, pB = marginal_from_joint(joint)
    P_A_given_B = conditional_A_given_B(joint, pB)
    P_B_given_A = conditional_B_given_A(joint, pA)

    # Compute entropies
    H_A = entropy_of_distribution(pA)
    H_B = entropy_of_distribution(pB)
    H_AB = joint_entropy(joint)
    H_A_given_B = conditional_entropy_A_given_B(joint, pB)
    H_B_given_A = conditional_entropy_B_given_A(joint, pA)

    # Formatted console outputs
    print("\n=== Матриця спільних ймовірностей P(A,B) ===\n")
    pretty_print_matrix(joint, title="P(A,B):")

    print("=== Маргінальні ймовірності ===")
    for i, val in enumerate(pA):
        print(f" P(A{i}) = {val:.6f}")
    print()
    for j, val in enumerate(pB):
        print(f" P(B{j}) = {val:.6f}")
    print()

    print("=== Умовні ймовірності ===")
    pretty_print_matrix(P_A_given_B, title="P(A|B) (колонки фіксують B):")
    pretty_print_matrix(P_B_given_A, title="P(B|A) (рядки фіксують A):")

    print("=== Ентропії (у бітах) ===")
    print(f"H(A)       = {H_A:.6f}")
    print(f"H(B)       = {H_B:.6f}")
    print(f"H(A,B)     = {H_AB:.6f}")
    print(f"H(A|B)     = {H_A_given_B:.6f}")
    print(f"H(B|A)     = {H_B_given_A:.6f}")
    print()

    print("=== Перевірка співвідношень ===")
    print(f"H(B) + H(A|B) = {H_B + H_A_given_B:.6f}")
    print(f"H(A) + H(B|A) = {H_A + H_B_given_A:.6f}")
    print(f"H(A,B) - H(A) = {H_AB - H_A:.6f}")
    print(f"H(A,B) - H(B) = {H_AB - H_B:.6f}")


if __name__ == "__main__":
    main()