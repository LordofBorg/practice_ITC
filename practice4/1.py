import numpy as np
from scipy.stats import binom
np.random.seed(42)
m = 9
p_for_bin = 0.25
t = 0.02 # біт/c
p_pom = 0.0005

np.set_printoptions(precision=6, suppress=True)

EPS = 1e-12  # уникнення log(0)

def normalize_matrix(mat):
    """Нормалізувати матрицю так, щоб сума елементів = 1."""
    s = np.sum(mat)
    if s <= 0:
        raise ValueError("Сума елементів матриці повинна бути > 0")
    return mat / s

def funk_zapov_matr_sumig_verog(target_row, target_col, init=None, max_iter=10000, tol=1e-9, eps=1e-12):
    """Створення сумісної матриці вірогідності множин, через матриці повної вірогідності множин"""
    target_row = np.asarray(target_row, dtype=float)
    target_col = np.asarray(target_col, dtype=float)

    # Перевірка сум маргіналей
    s_row = target_row.sum()
    s_col = target_col.sum()
    if not np.isclose(s_row, s_col):
        raise ValueError(f"Суми маргіналій не співпадають: sum(row)={s_row}, sum(col)={s_col}")

    m = len(target_row)
    n = len(target_col)
    if init is None:
        A = np.ones((m, n), dtype=float)
    else:
        A = np.array(init, dtype=float, copy=True)
        A[A <= 0] = eps

    for it in range(1, max_iter+1):
        # Рядки
        row_sums = A.sum(axis=1)

        # Запобігаєм ділення на 0
        row_sums[row_sums == 0] = eps
        A = (A.T * (target_row / row_sums)).T

        # стовбці
        col_sums = A.sum(axis=0)
        col_sums[col_sums == 0] = eps
        A = A * (target_col / col_sums)

        # Перевірка розбіжностей (максимальне відхилення)
        err_row = np.max(np.abs(A.sum(axis=1) - target_row))
        err_col = np.max(np.abs(A.sum(axis=0) - target_col))
        if err_row < tol and err_col < tol:
            return A

    return A

def zroblen_pov_verg_mnog(p):
    """Створення без умовної матриці множини за біноміальним розподілом"""
    # p_mnog = np.full(m, 0)
    # kilk = np.random.randint(1, 11, size=9)
    # n = np.sum(kilk)
    # for i in np.arange(0, m):
    #     promig = factorial(n)/(factorial(kilk[i])*factorial(n-kilk[i]))
    #     p_mnog[i] = promig*np.pow(p,kilk[i])*np.pow((1-p), (n-kilk[i]))
    # return p_mnog
    kilk = np.random.randint(1, 11, size=m)
    n = np.sum(kilk)
    # Вираховуємо вірогідність для кожного kilk[i] та приводимо суму до 1
    p_mnog = normalize_matrix(binom.pmf(kilk, n, p))
    return p_mnog

def conditional_A_given_B(joint, pB):
    """P(A|B) матриця: розмір 9x9, стовпці відповідають фіксованому b: P(A=a|B=b)."""
    cond = np.zeros_like(joint)
    for b in range(joint.shape[1]):
        if pB[b] > 0:
            cond[:, b] = joint[:, b] / pB[b]
        else:
            cond[:, b] = 0.0  # якщо pB[b]==0, умовний розподіл невизначений -> заповнимо нулями
    return cond

def conditional_B_given_A(joint, pA):
    """P(B|A) матриця: рядки відповідають фіксованому a: P(B=b|A=a)."""
    cond = np.zeros_like(joint)
    for a in range(joint.shape[0]):
        if pA[a] > 0:
            cond[a, :] = joint[a, :] / pA[a]
        else:
            cond[a, :] = 0.0
    return cond

def entropy_of_distribution(p):
    """Ентропія в бітах для вектор-розподілу p (1D)."""
    p = np.asarray(p, dtype=float)
    # Беремо тільки p>0
    p_nonzero = p[p > EPS]
    return -np.sum(p_nonzero * np.log2(p_nonzero))

def conditional_entropy_A_given_B(joint, pB):
    """H(A|B) = sum_b p(b) H(A|B=b)"""
    H = 0.0
    for b in range(joint.shape[1]):
        pb = pB[b]
        if pb > EPS:
            H_ab = entropy_of_distribution(joint[:, b])
            H += pb * H_ab
    return H

def conditional_entropy_B_given_A(joint, pA):
    """H(B|A) = sum_a p(a) H(B|A=a)"""
    H = 0.0
    for a in range(joint.shape[0]):
        pa = pA[a]
        if pa > EPS:
            H_ba = entropy_of_distribution(joint[a, :])
            H += pa * H_ba
    return H

def pretty_print_matrix(mat, row_labels=None, col_labels=None, title=None):
    if title:
        print(title)
    rows, cols = mat.shape
    # Заголовки
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



def main():
    # Створення матриць
    P_A = zroblen_pov_verg_mnog(p_for_bin)
    P_B = zroblen_pov_verg_mnog(p_for_bin)
    vipad_matr = normalize_matrix(np.random.rand(m, m))
    P_A_B = funk_zapov_matr_sumig_verog(P_A, P_B, vipad_matr)
    P_A_given_B = conditional_A_given_B(P_A_B, P_B)
    P_B_given_A = conditional_B_given_A(P_A_B, P_A)

    # Ентропії та інформація сумісних множин
    H_A = entropy_of_distribution(P_A)
    H_B = entropy_of_distribution(P_B)
    H_A_given_B = conditional_entropy_A_given_B(P_A_given_B, P_B)
    H_B_given_A = conditional_entropy_B_given_A(P_B_given_A, P_A)
    I_AB = H_A - H_A_given_B

    #Пропускна здатність з завадами те без завад
    C_bz_cher_H = np.log2(m)/t
    C_zz = (np.log2(m) + p_pom*np.log2(p_pom/(m-1)) + (1-p_pom)*np.log2(1-p_pom))/t

    # Друк результатів
    print("=== Маргінали ===")
    print("P(A) (для кожного рядка A_i):")
    for i, val in enumerate(P_A):
        print(f" A{i}: {val:.6f}")
    print()
    print("P(B) (для кожного стовпця B_j):")
    for j, val in enumerate(P_B):
        print(f" B{j}: {val:.6f}")
    print()

    print("=== Умовні ймовірності ===")
    pretty_print_matrix(P_A_given_B, title="P(A|B)  (колонки фіксують B):")
    pretty_print_matrix(P_B_given_A, title="P(B|A)  (рядки фіксують A):")

    print("=== Ентропії (в бітах) ===")
    print(f"H(A)       = {H_A:.6f} бит")
    print(f"H(B)       = {H_B:.6f} бит")
    print(f"H(A|B)     = {H_A_given_B:.6f} бит   (обчислено як sum_b p(b) H(A|B=b))")
    print(f"H(B|A)     = {H_B_given_A:.6f} бит   (обчислено як sum_a p(a) H(B|A=a))")
    print()

    print("=== Кількість інформації (в бітах) ===")
    print(f"I(A,B) = {I_AB:.6f}")

    print("=== Пропускна здатність каналу (в біт/ceк) ===")
    print(f"Без завад через формулу C=H(max)/t   C = {C_bz_cher_H:.6f}")
    print(f"З завадами через формулу C=(log2(m) + log2(1/(m*P)) + (1-P)*log2(1-P))/t, де Р = вірогідність помилки \nC = {C_zz:.6f}")

if __name__ == "__main__":
    main()