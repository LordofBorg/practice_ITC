import heapq
import math
import itertools
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Any

# Input probabilities
P1 = 0.82
P2 = 1.0 - P1


class HuffmanNode:
    def __init__(self, symbol: Optional[str], prob: float) -> None:
        self.symbol: Optional[str] = symbol
        self.prob: float = prob
        self.left: Optional[HuffmanNode] = None
        self.right: Optional[HuffmanNode] = None

    def __lt__(self, other: 'HuffmanNode') -> bool:
        # Stable sorting sorting by value, fallback to symbol name
        if abs(self.prob - other.prob) < 1e-9:
            s1 = self.symbol if self.symbol else ""
            s2 = other.symbol if other.symbol else ""
            return s1 < s2
        return self.prob < other.prob


def build_huffman_codes(prob_dict: Dict[str, float]) -> Dict[str, str]:
    """Builds Huffman codebook from a dictionary mapping symbols to probabilities."""
    heap = [HuffmanNode(sym, prob) for sym, prob in prob_dict.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = HuffmanNode(None, left.prob + right.prob)
        parent.left = left
        parent.right = right
        heapq.heappush(heap, parent)

    codes: Dict[str, str] = {}

    def traverse(node: Optional[HuffmanNode], code: str) -> None:
        if node is None:
            return
        if node.symbol is not None:
            codes[node.symbol] = code
            return
        traverse(node.left, code + "0")
        traverse(node.right, code + "1")

    traverse(heap[0], "")
    return codes


def run_analysis() -> None:
    """Performs Huffman coding analysis on block lengths L=1..4."""
    print(f"Вхідні дані: p(x1)={P1}, p(x2)={P2:.2f}\n")
    base_probs = {'x1': P1, 'x2': P2}

    # Playlists for charting
    L_values: List[int] = []
    H_max_values: List[float] = []
    real_H_values: List[float] = []
    n_avg_values: List[float] = []
    nc_values: List[float] = []
    chi_d_values: List[float] = []
    chi_k_values: List[float] = []

    summary_table: List[List[Any]] = []

    for L in range(1, 5):
        # Generate block combinations
        block_probs: Dict[str, float] = {}
        for combo in itertools.product(['x1', 'x2'], repeat=L):
            name = "·".join(combo)
            prob = 1.0
            for sym in combo:
                prob *= base_probs[sym]
            block_probs[name] = prob

        # Generate Huffman codes
        huff_codes = build_huffman_codes(block_probs)

        current_avg_len = 0.0
        current_entropy = 0.0
        min_len = float('inf')

        sorted_blocks = sorted(block_probs.items(), key=lambda item: item[1], reverse=True)

        print(f"--- Таблиця {L} (L={L}) ---")
        print(f"{'Комбінація':<15} | {'P(xk)':<10} | {'Код':<10} | {'len':<5}")
        print("-" * 50)

        for symbol, prob in sorted_blocks:
            code = huff_codes[symbol]
            length = len(code)
            current_avg_len += prob * length
            if prob > 0:
                current_entropy -= prob * math.log2(prob)
            if length < min_len:
                min_len = length
            print(f"{symbol:<15} | {prob:.5f}    | {code:<10} | {length:<5}")
        print("\n")

        # Code efficiency parameters
        H_max = float(L)
        nc = current_avg_len / L
        chi_d = 1.0 - (current_entropy / H_max)
        chi_k = 1.0 - (current_entropy / current_avg_len)

        # Append variables for matplotlib plots
        L_values.append(L)
        H_max_values.append(H_max)
        real_H_values.append(current_entropy)
        n_avg_values.append(current_avg_len)
        nc_values.append(nc)
        chi_d_values.append(chi_d)
        chi_k_values.append(chi_k)

        summary_table.append([L, current_entropy, min_len, current_avg_len, nc, chi_d, chi_k])

    # Table 5 summary display
    print("=" * 95)
    print(f"{'Таблиця 5 (Повна)':^95}")
    print("=" * 95)
    headers = ["L", "H(S)", "n_min", "n (cep)", "nc (sym)", "χд (source)", "χк (code)"]
    print(
        f"{headers[0]:<3} | {headers[1]:<10} | {headers[2]:<6} | {headers[3]:<10} | {headers[4]:<10} | {headers[5]:<12} | {headers[6]:<12}"
    )
    print("-" * 95)
    for row in summary_table:
        print(
            f"{row[0]:<3} | {row[1]:<10.5f} | {row[2]:<6} | {row[3]:<10.5f} | {row[4]:<10.5f} | {row[5]:<12.5f} | {row[6]:<12.5f}"
        )
    print("-" * 95)

    # 1. Entropy plot
    plt.figure(figsize=(10, 6))
    plt.plot(L_values, H_max_values, 'o--', label='Hmax(S) = L (Теоретична)', color='blue')
    plt.plot(L_values, real_H_values, 's-', label='H(S) (Реальна)', color='green')
    plt.title('Залежність ентропії від довжини блоку L')
    plt.xlabel('L (кількість символів у блоці)')
    plt.ylabel('Ентропія (біт)')
    plt.xticks(L_values)
    plt.legend()
    plt.grid(True)

    # 2. Code Length plot
    plt.figure(figsize=(10, 6))
    plt.plot(L_values, n_avg_values, 'o-', label='n_cep (середня довжина блоку)', color='red')
    plt.plot(L_values, nc_values, 's--', label='nc (середня довжина на символ)', color='orange')
    plt.title('Залежність довжини коду від L')
    plt.xlabel('L (кількість символів у блоці)')
    plt.ylabel('Довжина (біт)')
    plt.xticks(L_values)
    plt.legend()
    plt.grid(True)

    # 3. Redundancy coefficients plot
    plt.figure(figsize=(10, 6))
    plt.plot(L_values, chi_d_values, 'o-', label='χд (Надмірність джерела)', color='purple')
    plt.plot(L_values, chi_k_values, 's-', label='χк (Надмірність коду)', color='brown')
    plt.title('Залежність коефіцієнтів надмірності від L')
    plt.xlabel('L (кількість символів у блоці)')
    plt.ylabel('Коефіцієнт')
    plt.xticks(L_values)
    plt.legend()
    plt.grid(True)

    print("\nГрафіки побудовано у 3-х окремих вікнах.")
    plt.show()


if __name__ == "__main__":
    run_analysis()