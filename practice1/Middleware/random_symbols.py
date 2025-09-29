import random

# Списки символів для кожної мови
ukrainian_chars = "абвгдеєжзиіїйклмнопрстуфхцчшщьюяАБВГҐДЕЄЖЗИЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ " \
                  " ,.!?()"
german_chars = "abcdefghijklmnopqrstuvwxyzäöüßABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜß " \
               " ,.!?()"
english_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ " \
                " ,.!?()"

# Функція для генерації випадкового тексту з символами конкретної мови
def generate_random_text(language_chars, length):
    return ''.join(random.choice(language_chars) for _ in range(length))

# Генерація тексту для кожної мови
ukrainian_text = generate_random_text(ukrainian_chars, 1500)
german_text = generate_random_text(german_chars, 1500)
english_text = generate_random_text(english_chars, 1500)

# Виведення результату
print("Текст українською:")
print(ukrainian_text)
print("\nТекст німецькою:")
print(german_text)
print("\nТекст англійською:")
print(english_text)
