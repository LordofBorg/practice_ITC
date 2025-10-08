"""
Обчислює ентропійні величини H(A), H(B), H(A,B), H(B|A), H(A|B)
на основі заданої матриці спільних ймовірностей P(A,B).
"""
import numpy as np

# Налаштування відображення чисел: 6 знаків після коми, без наукової нотації
np.set_printoptions(precision=6, suppress=True)

# уникнення log(0)
EPS = 1e-12

def normalize_matrix(mat):
    """Нормалізувати матрицю так, щоб сума елементів = 1."""
    s = np.sum(mat)
    if s <= 0:
        raise ValueError("Сума елементів матриці повинна бути > 0")
    return mat / s

# --- 1. Обчислення маргінальних ймовірностей ---
def marginal_from_joint(joint):
    """Отримати маргінали P(A) (рядки) та P(B) (стовпці) з P(A,B)."""
    pA = np.sum(joint, axis=1)  # сума по стовпцях -> для кожного рядка
    pB = np.sum(joint, axis=0)  # сума по рядках -> для кожного стовпця
    return pA, pB

# --- 2. Умовні ймовірності ---
def conditional_A_given_B(joint, pB):
    """Обчислює умовні ймовірності P(A|B), колонки відповідають фіксованому B."""
    cond = np.zeros_like(joint)
    for b in range(joint.shape[1]):
        if pB[b] > 0:
            cond[:, b] = joint[:, b] / pB[b]
        else:
            cond[:, b] = 0.0  # якщо P(B=b)=0 -> заповнюємо нулями
    return cond

def conditional_B_given_A(joint, pA):
    """Обчислює умовні ймовірності P(B|A), рядки відповідають фіксованому A."""
    cond = np.zeros_like(joint)
    for a in range(joint.shape[0]):
        if pA[a] > 0:
            cond[a, :] = joint[a, :] / pA[a]
        else:
            cond[a, :] = 0.0
    return cond

# --- 3. Ентропії ---
def entropy_of_distribution(p):
    """H(A), ентропія для одномірного розподілу p (у бітах)."""
    p = np.asarray(p, dtype=float)
    # Беремо тільки p>0
    p_nonzero = p[p > EPS]
    return -np.sum(p_nonzero * np.log2(p_nonzero))

def joint_entropy(joint):
    """H(A,B), спільна ентропія двох змінних."""
    flat = joint.flatten()
    flat_nz = flat[flat > EPS]
    return -np.sum(flat_nz * np.log2(flat_nz))

# --- 4. Умовні ентропії ---
def conditional_entropy_A_given_B(joint, pB):
    """H(B|A) = Σ_a p(a) * H(B|A=a)"""
    H = 0.0
    for b in range(joint.shape[1]):
        pb = pB[b]
        if pb > EPS:
            pA_given_b = joint[:, b] / pb
            H_ab = entropy_of_distribution(pA_given_b)
            H += pb * H_ab
    return H

def conditional_entropy_B_given_A(joint, pA):
    """H(B|A) = Σ_a p(a) * H(B|A=a)"""
    H = 0.0
    for a in range(joint.shape[0]):
        pa = pA[a]
        if pa > EPS:
            pB_given_a = joint[a, :] / pa
            H_ba = entropy_of_distribution(pB_given_a)
            H += pa * H_ba
    return H

# ================== ВИВІД ==================
def pretty_print_matrix(mat, row_labels=None, col_labels=None, title=None):
    """Друкує матрицю з підписами рядків і стовпців."""
    if title:
        print(title)
    rows, cols = mat.shape
    # заголовки
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

# ================== ГОЛОВНА ПРОГРАМА ==================
def main():
    np.random.seed(1337)  # щоб приклад був відтворюваний

    # Варіант 2: випадкова матриця ймовірностей 9x9
    rand = np.random.rand(9, 9)
    joint = normalize_matrix(rand)

    # Отримуємо всі необхідні розподіли
    pA, pB = marginal_from_joint(joint)
    P_A_given_B = conditional_A_given_B(joint, pB)
    P_B_given_A = conditional_B_given_A(joint, pA)

    # Обчислення ентропій
    H_A = entropy_of_distribution(pA)
    H_B = entropy_of_distribution(pB)
    H_AB = joint_entropy(joint)
    H_A_given_B = conditional_entropy_A_given_B(joint, pB)
    H_B_given_A = conditional_entropy_B_given_A(joint, pA)

    # === Вивід результатів ===
    print("\n=== Матриця спільних ймовірностей P(A,B) ===\n")
    pretty_print_matrix(joint, title="P(A,B):")

    print("=== Маргінали ===")
    for i, val in enumerate(pA):
        print(f" P(A{i}) = {val:.6f}")
    print()
    for j, val in enumerate(pB):
        print(f" P(B{j}) = {val:.6f}")
    print()

    print("=== Умовні ймовірності ===")
    pretty_print_matrix(P_A_given_B, title="P(A|B):  колонки фіксують B")
    pretty_print_matrix(P_B_given_A, title="P(B|A):  рядки фіксують A")

    print("=== Ентропії (у бітах) ===")
    print(f"H(A)       = {H_A:.6f}")
    print(f"H(B)       = {H_B:.6f}")
    print(f"H(A,B)     = {H_AB:.6f}")
    print(f"H(A|B)     = {H_A_given_B:.6f}")
    print(f"H(B|A)     = {H_B_given_A:.6f}")
    print()

    # Перевірка основних співвідношень
    print("=== Перевірка співвідношень ===")
    print(f"H(B) + H(A|B) = {H_B + H_A_given_B:.6f}")
    print(f"H(A) + H(B|A) = {H_A + H_B_given_A:.6f}")
    print(f"H(A,B) - H(A) = {H_AB - H_A:.6f}")
    print(f"H(A,B) - H(B) = {H_AB - H_B:.6f}")

if __name__ == "__main__":
    main()