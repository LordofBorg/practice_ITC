import random

# Character sets for generating noise texts imitating specific alphabets
ukrainian_chars = (
    "абвгдеєжзиіїйклмнопрстуфхцчшщьюя"
    "АБВГҐДЕЄЖЗИЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ "
    " ,.!?()"
)

german_chars = (
    "abcdefghijklmnopqrstuvwxyzäöüß"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜß "
    " ,.!?()"
)

english_chars = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
    " ,.!?()"
)


def generate_random_text(language_chars: str, length: int) -> str:
    """Generates a pseudo-random character sequence of specified length from the alphabet."""
    return ''.join(random.choice(language_chars) for _ in range(length))


def main() -> None:
    ukrainian_text = generate_random_text(ukrainian_chars, 1500)
    german_text = generate_random_text(german_chars, 1500)
    english_text = generate_random_text(english_chars, 1500)

    print("Текст українською:")
    print(ukrainian_text)
    print("\nТекст німецькою:")
    print(german_text)
    print("\nТекст англійською:")
    print(english_text)


if __name__ == "__main__":
    main()
