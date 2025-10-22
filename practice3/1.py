from math import log2, sqrt
# -----------------------------
# ЗАДАЧА 1. Обчислення ентропії
# -----------------------------
N_1 = 22
# У першому випадку (А) в нас верогідність символу однакова(рівномірна) тому можно використати формулу Н = log2(N)
P_a_1 = 1/N_1
H_a_1 = log2(N_1)
# У другому випадку обчислення проводемо ха допомогою шенона
P_b_1 = [0.5 ** i for i in range(1, N_1 + 1)]
P_b_1[N_1-1] += 0.5 ** (N_1)
H_b_1 = -sum(P_b_1[b]*log2(P_b_1[b]) for b in range(len(P_b_1)) if P_b_1[b]!=0)
print("=== ЗАДАЧА 1 ===")
print(f"Кількість символів k = {N_1}")
print(f"Ймовірність символів при рівноймовірних символах: P_a = {P_a_1:.8f}")
print(f"Ентропія при рівноймовірних символах: H_a = {H_a_1:.8f} біт/символ")
print(f"Ймовірність символів за законом,  p(i) = (1/2)^i:")
for i in range(N_1): print(f"   Елемент({i+1}):  Р={P_b_1[i]:.10f};")
print(f"Ентропія при нерівноймовірних символах: H2 = {H_b_1:.8f} біт/символ\n")

# -----------------------------------
# ЗАДАЧА 2. Недовантаженість символів
# -----------------------------------
R_b_1 = 1-H_b_1/log2(N_1)
print("=== ЗАДАЧА 2 ===")
print(f"Недовантаженість при нерівноймовірних символах варіанту (б){R_b_1}\n")

# -----------------------------------
# ЗАДАЧА 3. Знайти швидкість передавання повідомлень
# -----------------------------------
N_2 = 12
P_a_2 = 1/N_2
P_b_2 = [0.5 ** i for i in range(1, N_2 + 1)]
P_b_2[N_2-1] += 0.5 ** (N_2)
H_a_2 = -log2(P_a_2)
H_b_2 = -sum(P_b_2[b]*log2(P_b_2[b]) for b in range(len(P_b_2)) if P_b_2[b]!=0)
t = range(1,N_2+1)
S_t_a = sum(P_a_2*t[i] for i in range(12))
V_a = H_a_2/S_t_a
S_t_b = sum(P_b_2[i]*t[i] for i in range(12))
V_b = H_b_2/S_t_b
print("=== ЗАДАЧА 3 ===")
print(f"Кількість символів k = {N_2}")
print(f"Ймовірність символів при рівноймовірних символах: P_a = {P_a_2:.8f}")
print(f"Ентропія при рівноймовірних символах: H_a = {H_a_2:.8f} біт/символ")
print(f"Середня швидкість передавання символа: {S_t_a}cим/сек")
print(f"Швидкість передавання повідомлень: R={V_a}біт/сек")
print(f"Ймовірність символів за законом,  p(i) = (1/2)^i:")
for i in range(N_2): print(f"   Елемент({i+1}):  Р={P_b_2[i]:.10f};")
print(f"Ентропія при нерівноймовірних символах: H2 = {H_b_2:.8f} біт/символ\n")
print(f"Середня швидкість передавання символа: {S_t_b}cим/сек")
print(f"Швидкість передавання повідомлень: R={V_b}біт/сек\n")

# -----------------------------------
# ЗАДАЧА 4. Побудувати оптимальний код повідомлення з використанням методу Шеннона-Фано
# -----------------------------------

def shannon_fano(symbols, probabilities):
    """Побудова кодів методом Шеннона–Фано"""
    codes = {sym: "" for sym in symbols}

    def recursive_build(symbols, probs):
        if len(symbols) == 1:
            return
        total = sum(probs)
        acc = 0
        split_index = 0
        for i, p in enumerate(probs):
            acc += p
            if acc >= total / 2:
                split_index = i
                break
        left = symbols[:split_index+1]
        right = symbols[split_index+1:]
        for sym in left:
            codes[sym] += "0"
        for sym in right:
            codes[sym] += "1"
        recursive_build(left, probs[:split_index+1])
        recursive_build(right, probs[split_index+1:])

    recursive_build(symbols, probabilities)
    return codes

#Функція шифрування тексту
def koduv_text(text, table):
    result = ""
    for i in text:
        result += table[i]+" "
    return result

#Функція дешифрування тексту
def dekoduv_text(text, table):
    result = ""
    s = text.split(" ")
    for i in range(len(s)-1):
        result += table[s[i]]
    return result

simv = [f"a{i}" for i in range(1, N_2+1)]
verog = [0.5 ** i for i in range(1, N_2 + 1)]
verog[N_2-1] += 0.5 ** (N_2)
slov_for_koder = shannon_fano(simv,verog)
list_kod = list(slov_for_koder.values())

print("=== ЗАДАЧА 4 ===")
print("\nДемонстрація згенерованих потрібних кодів:")
a=int((len(list_kod)/6)//1)
for i in range(a):
    print(list_kod[6*i:6*i+6])
print(list_kod[a*6 :])
print("\nДемонстрація словника для кодування:")
a=int((len(slov_for_koder)/6)//1)
for i in range(a):
    print(list(slov_for_koder.items())[6*i:6*i+6])
print(list(slov_for_koder.items())[a*6 :])