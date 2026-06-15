import numpy as np
from scipy.stats import binom
from typing import Optional, Tuple, List

# Reproducible results
np.random.seed(42)

m = 9
p_for_bin = 0.25
t = 0.02       # symbol duration in seconds
p_pom = 0.0005  # error probability

np.set_printoptions(precision=6, suppress=True)
EPS = 1e-12


def normalize_matrix(mat: np.ndarray) -> np.ndarray:
    """Normalizes the matrix elements to sum up to 1."""
    s = np.sum(mat)
    if s <= 0:
        raise ValueError("Matrix elements sum must be greater than zero.")
    return mat / s


def funk_zapov_matr_sumig_verog(
    target_row: np.ndarray,
    target_col: np.ndarray,
    init: Optional[np.ndarray] = None,
    max_iter: int = 10000,
    tol: float = 1e-9,
    eps: float = 1e-12
) -> np.ndarray:
    """
    Computes the joint probability matrix that satisfies row and column marginal bounds
    using the Iterative Proportional Fitting (IPF) / Sinkhorn-Knopp algorithm.
    """
    target_row = np.asarray(target_row, dtype=float)
    target_col = np.asarray(target_col, dtype=float)

    s_row = target_row.sum()
    s_col = target_col.sum()
    if not np.isclose(s_row, s_col):
        raise ValueError(f"Marginal sum mismatch: sum(row)={s_row}, sum(col)={s_col}")

    rows_count = len(target_row)
    cols_count = len(target_col)
    if init is None:
        A = np.ones((rows_count, cols_count), dtype=float)
    else:
        A = np.array(init, dtype=float, copy=True)
        A[A <= 0] = eps

    for it in range(1, max_iter + 1):
        # Row normalization step
        row_sums = A.sum(axis=1)
        row_sums[row_sums == 0] = eps
        A = (A.T * (target_row / row_sums)).T

        # Column normalization step
        col_sums = A.sum(axis=0)
        col_sums[col_sums == 0] = eps
        A = A * (target_col / col_sums)

        # Check convergence bounds
        err_row = np.max(np.abs(A.sum(axis=1) - target_row))
        err_col = np.max(np.abs(A.sum(axis=0) - target_col))
        if err_row < tol and err_col < tol:
            return A

    return A


def zroblen_pov_verg_mnog(p: float) -> np.ndarray:
    """Generates a normalized marginal probability vector using the binomial distribution."""
    kilk = np.random.randint(1, 11, size=m)
    n = np.sum(kilk)
    # Calculate binomial PMF for each count value
    p_mnog = normalize_matrix(binom.pmf(kilk, n, p))
    return p_mnog


def conditional_A_given_B(joint: np.ndarray, pB: np.ndarray) -> np.ndarray:
    """Computes the conditional probability matrix P(A|B)."""
    cond = np.zeros_like(joint)
    for b in range(joint.shape[1]):
        if pB[b] > 0:
            cond[:, b] = joint[:, b] / pB[b]
        else:
            cond[:, b] = 0.0
    return cond


def conditional_B_given_A(joint: np.ndarray, pA: np.ndarray) -> np.ndarray:
    """Computes the conditional probability matrix P(B|A)."""
    cond = np.zeros_like(joint)
    for a in range(joint.shape[0]):
        if pA[a] > 0:
            cond[a, :] = joint[a, :] / pA[a]
        else:
            cond[a, :] = 0.0
    return cond


def entropy_of_distribution(p: np.ndarray) -> float:
    """Computes the Shannon entropy of a 1D probability distribution in bits."""
    p_arr = np.asarray(p, dtype=float)
    p_nonzero = p_arr[p_arr > EPS]
    return float(-np.sum(p_nonzero * np.log2(p_nonzero)))


def conditional_entropy_A_given_B(joint: np.ndarray, pB: np.ndarray) -> float:
    """Computes the conditional entropy H(A|B) = sum_b P(b) * H(A|B=b) in bits."""
    H = 0.0
    for b in range(joint.shape[1]):
        pb = pB[b]
        if pb > EPS:
            H_ab = entropy_of_distribution(joint[:, b])
            H += pb * H_ab
    return float(H)


def conditional_entropy_B_given_A(joint: np.ndarray, pA: np.ndarray) -> float:
    """Computes the conditional entropy H(B|A) = sum_a P(a) * H(B|A=a) in bits."""
    H = 0.0
    for a in range(joint.shape[0]):
        pa = pA[a]
        if pa > EPS:
            H_ba = entropy_of_distribution(joint[a, :])
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
    # Build marginals and joint probability matrices
    P_A = zroblen_pov_verg_mnog(p_for_bin)
    P_B = zroblen_pov_verg_mnog(p_for_bin)
    random_base = normalize_matrix(np.random.rand(m, m))
    
    P_A_B = funk_zapov_matr_sumig_verog(P_A, P_B, random_base)
    P_A_given_B = conditional_A_given_B(P_A_B, P_B)
    P_B_given_A = conditional_B_given_A(P_A_B, P_A)

    # Compute entropies and mutual information
    H_A = entropy_of_distribution(P_A)
    H_B = entropy_of_distribution(P_B)
    H_A_given_B = conditional_entropy_A_given_B(P_A_given_B, P_B)
    H_B_given_A = conditional_entropy_B_given_A(P_B_given_A, P_A)
    I_AB = H_A - H_A_given_B

    # Compute channel capacity with and without noise
    C_bz_cher_H = np.log2(m) / t
    C_zz = (np.log2(m) + p_pom * np.log2(p_pom / (m - 1)) + (1 - p_pom) * np.log2(1 - p_pom)) / t

    # Print results to console
    print("=== Маргінальні розподіли ===")
    print("P(A) (для кожного рядка A_i):")
    for i, val in enumerate(P_A):
        print(f" A{i}: {val:.6f}")
    print()
    print("P(B) (для кожного стовпця B_j):")
    for j, val in enumerate(P_B):
        print(f" B{j}: {val:.6f}")
    print()

    print("=== Умовні ймовірності ===")
    pretty_print_matrix(P_A_given_B, title="P(A|B) (колонки фіксують B):")
    pretty_print_matrix(P_B_given_A, title="P(B|A) (рядки фіксують A):")

    print("=== Ентропії (в бітах) ===")
    print(f"H(A)       = {H_A:.6f} біт")
    print(f"H(B)       = {H_B:.6f} біт")
    print(f"H(A|B)     = {H_A_given_B:.6f} біт (обчислено як sum_b p(b) H(A|B=b))")
    print(f"H(B|A)     = {H_B_given_A:.6f} біт (обчислено як sum_a p(a) H(B|A=a))")
    print()

    print("=== Кількість взаємної інформації (в бітах) ===")
    print(f"I(A,B) = {I_AB:.6f}")

    print("=== Пропускна здатність каналу (в біт/ceк) ===")
    print(f"Без завад через формулу C=H(max)/t:   C = {C_bz_cher_H:.6f}")
    print(f"З завадами через формулу C для симетричного каналу: C = {C_zz:.6f}")


if __name__ == "__main__":
    main()