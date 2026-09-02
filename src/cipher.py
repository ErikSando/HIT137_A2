from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent



while True:
    try:
        shift1 = int(input("Enter shift1 (non negative number): "))
        shift2 = int(input("Enter shift2 (non negative number): "))

        if shift1 >= 0 and shift2 >= 0:
            break

        print("Both values should be non-negative.")

    except ValueError:
        print("Please enter numbers only")

raw_text_path = BASE_DIR / "res" / "raw_text.txt"
encrypted_text_path = BASE_DIR / "res" / "encrypted_text.txt"
decrypted_text_path = BASE_DIR / "res" / "decrypted_text.txt"

#Reads from "raw_text.txt" and writes encrypted content to "encrypted_text.txt" .
def encrypt_file(shift1: int, shift2: int, input_path: str, output_path: str) -> None:
    encrypted_text = ""
    with open(input_path, "r") as raw_text_file:
        raw_text = raw_text_file.read()

    for ch in raw_text:
        # Lowercase Letters Encryption
        if 'a' <= ch <= 'n':
            shift = shift1 * shift2
            shifted_ch = chr((ord(ch) - ord('a') + shift) % 14 + ord('a'))
            encrypted_text += shifted_ch

        elif 'o' <= ch <= 'z':
            shift = shift1 + shift2
            shifted_ch = chr((ord(ch) - ord('o') - shift) % 12 + ord('o'))
            encrypted_text += shifted_ch

        # Uppercase Letters Encryption
        elif 'A' <= ch <= 'M':
            shift = shift1
            shifted_ch = chr((ord(ch) - ord('A') - shift) % 13 + ord('A'))
            encrypted_text+=shifted_ch

        elif 'N' <= ch <= 'Z':
            shift = shift2 ** 2
            shifted_ch = chr((ord(ch) - ord('N') + shift) % 13 + ord('N'))
            encrypted_text+=shifted_ch

        # Numbers Encryption
        elif '0' <= ch <= '9':
            shift = shift1 - shift2
            shifted_num = chr((ord(ch) - ord('0') + shift) % 10 + ord('0'))
            encrypted_text+=shifted_num

        else:
            encrypted_text+=ch

    with open(output_path, "w") as encrypt_text_file:
        encrypt_text_file.write(encrypted_text)


encrypt_file(shift1, shift2, raw_text_path, encrypted_text_path)
print("Encryption Completed")

# Compares "raw_text.txt" with "decrypted_text.txt" and prints whether the
#decryption was successful or not.
def verify_files(original_path: str, decrypted_path: str) -> bool:
    with open(original_path, "r") as raw_text_file:
        raw_text = raw_text_file.read()

    with open(decrypted_path, "r") as decrypted_text_file:
        decrypt_text = decrypted_text_file.read()

    if raw_text == decrypt_text:
        print("Decryption Successful")
    else:
        print("Decryption not Successful")


verify_files(raw_text_path, decrypted_text_path)
