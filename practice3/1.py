from math import log2
from typing import List, Dict

# Input parameters
N_1 = 22
N_2 = 12


def shannon_fano(symbols: List[str], probabilities: List[float]) -> Dict[str, str]:
    """
    Constructs optimal prefix codes for the given symbols using the Shannon-Fano algorithm.
    """
    codes = {sym: "" for sym in symbols}

    def recursive_build(syms: List[str], probs: List[float]) -> None:
        if len(syms) <= 1:
            return
        total = sum(probs)
        acc = 0.0
        split_index = 0
        for i, p in enumerate(probs):
            acc += p
            if acc >= total / 2.0:
                split_index = i
                break
        
        # In case the split falls on the boundary
        if split_index == len(syms) - 1:
            split_index = len(syms) - 2

        left = syms[:split_index + 1]
        right = syms[split_index + 1:]
        for sym in left:
            codes[sym] += "0"
        for sym in right:
            codes[sym] += "1"

        recursive_build(left, probs[:split_index + 1])
        recursive_build(right, probs[split_index + 1:])

    recursive_build(symbols, probabilities)
    return codes


def koduv_text(text: str, table: Dict[str, str]) -> str:
    """Encodes a string using the Shannon-Fano codebook."""
    return " ".join(table[char] for char in text if char in table)


def dekoduv_text(text: str, table: Dict[str, str]) -> str:
    """Decodes a binary sequence using the reverse Shannon-Fano codebook."""
    reverse_table = {v: k for k, v in table.items()}
    return "".join(reverse_table[code] for code in text.split(" ") if code in reverse_table)


def main() -> None:
    # -----------------------------
    # TASK 1: Entropy Computation
    # -----------------------------
    # Case A: Uniform probability distribution H = log2(N)
    P_a_1 = 1.0 / N_1
    H_a_1 = log2(N_1)

    # Case B: Non-uniform distribution p(i) = 2^(-i) with normalization
    P_b_1 = [0.5 ** i for i in range(1, N_1 + 1)]
    P_b_1[N_1 - 1] += 0.5 ** N_1
    H_b_1 = -sum(p * log2(p) for p in P_b_1 if p > 0)

    print("=== ЗАДАЧА 1 ===")
    print(f"Кількість символів k = {N_1}")
    print(f"Ймовірність при рівноймовірних символах: P_a = {P_a_1:.8f}")
    print(f"Ентропія при рівноймовірних символах: H_a = {H_a_1:.8f} біт/символ")
    print("Ймовірність символів за нерівномірним законом p(i) = (1/2)^i:")
    for i in range(N_1):
        print(f"   Елемент({i+1}): Р = {P_b_1[i]:.10f};")
    print(f"Ентропія при нерівноймовірних символах: H_b = {H_b_1:.8f} біт/символ\n")

    # -----------------------------------
    # TASK 2: Source Redundancy (Under-utilization)
    # -----------------------------------
    R_b_1 = 1.0 - (H_b_1 / log2(N_1))
    print("=== ЗАДАЧА 2 ===")
    print(f"Недовантаженість джерела при нерівноймовірних символах: R = {R_b_1:.8f}\n")

    # -----------------------------------
    # TASK 3: Message Transmission Speed
    # -----------------------------------
    P_a_2 = 1.0 / N_2
    P_b_2 = [0.5 ** i for i in range(1, N_2 + 1)]
    P_b_2[N_2 - 1] += 0.5 ** N_2

    H_a_2 = -log2(P_a_2)
    H_b_2 = -sum(p * log2(p) for p in P_b_2 if p > 0)

    t_duration = list(range(1, N_2 + 1))
    
    # Average symbol duration
    S_t_a = sum(P_a_2 * t_duration[i] for i in range(N_2))
    V_a = H_a_2 / S_t_a

    S_t_b = sum(P_b_2[i] * t_duration[i] for i in range(N_2))
    V_b = H_b_2 / S_t_b

    print("=== ЗАДАЧА 3 ===")
    print(f"Кількість символів k = {N_2}")
    print(f"Ймовірність при рівноймовірних символах: P_a = {P_a_2:.8f}")
    print(f"Ентропія при рівноймовірних символах: H_a = {H_a_2:.8f} біт/символ")
    print(f"Середня тривалість передачі символу: {S_t_a:.2f} сек")
    print(f"Швидкість передачі повідомлень: R = {V_a:.6f} біт/сек\n")
    print("Ймовірність символів за нерівномірним законом:")
    for i in range(N_2):
        print(f"   Елемент({i+1}): Р = {P_b_2[i]:.10f};")
    print(f"Ентропія при нерівноймовірних символах: H_b = {H_b_2:.8f} біт/символ")
    print(f"Середня тривалість передачі символу: {S_t_b:.2f} сек")
    print(f"Швидкість передачі повідомлень: R = {V_b:.6f} біт/сек\n")

    # -----------------------------------
    # TASK 4: Shannon-Fano Coding
    # -----------------------------------
    simv = [f"a{i}" for i in range(1, N_2 + 1)]
    verog = [0.5 ** i for i in range(1, N_2 + 1)]
    verog[N_2 - 1] += 0.5 ** N_2

    slov_for_koder = shannon_fano(simv, verog)
    list_kod = list(slov_for_koder.values())

    print("=== ЗАДАЧА 4 ===")
    print("\nДемонстрація згенерованих префіксних кодів:")
    chunk_size = 6
    for i in range(0, len(list_kod), chunk_size):
        print(list_kod[i:i+chunk_size])

    print("\nДемонстрація словника для кодування:")
    items_list = list(slov_for_koder.items())
    for i in range(0, len(items_list), chunk_size):
        print(items_list[i:i+chunk_size])


if __name__ == "__main__":
    main()