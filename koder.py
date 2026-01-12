import string
import random
import base64
import os
import colorama
from colorama import Fore, Style

# Inicjalizacja kolorów dla Windowsa
colorama.init(autoreset=True)


class WinterCoder:
    def __init__(self, seed_str="default"):
        # Bazowa lista znaków (zgodnie z Twoim pierwotnym kodem)
        self.base_charset = (
                string.digits +
                string.ascii_letters +
                string.punctuation +
                " " + "ą ć ę ł ń ó ś ź ż"
        )
        self.base_charset = (self.base_charset + "?" * 128)[:128]
        self.current_charset = self.apply_seed(seed_str)

        self.char_to_bin = {char: format(i, '07b') for i, char in enumerate(self.current_charset)}
        self.bin_to_char = {format(i, '07b'): char for i, char in enumerate(self.current_charset)}

    def apply_seed(self, seed_str):
        char_list = list(self.base_charset)
        random.seed(seed_str)
        random.shuffle(char_list)
        return "".join(char_list)

    def encode(self, text):
        return "".join(self.char_to_bin.get(c, '0000000') for c in text)

    def decode(self, binary_str):
        return "".join(self.bin_to_char.get(binary_str[i:i + 7], '?') for i in range(0, len(binary_str), 7))


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def show_menu():
    clear_console()
    print(f"{Fore.CYAN}{'=' * 40}")
    print(f"{Fore.CYAN}       Barońska Koder")
    print(f"{Fore.CYAN}{'=' * 40}{Style.RESET_ALL}")
    print(f"[{Fore.GREEN}1{Style.RESET_ALL}] ZAKODUJ wiadomość")
    print(f"[{Fore.GREEN}2{Style.RESET_ALL}] ODKODUJ wiadomość")
    print(f"[{Fore.RED}0{Style.RESET_ALL}] Wyjdź z programu")
    print(f"{Fore.CYAN}{'=' * 40}{Style.RESET_ALL}")
    print(f"{Fore.BLACK}Baronska 2026©. v.2-d")

def main():
    while True:
        show_menu()
        wybor = input(f"{Fore.YELLOW}Wybierz opcję (1/2/0): {Style.RESET_ALL}").strip()

        if wybor == '0':
            print(f"{Fore.MAGENTA}Zamykanie... Do zobaczenia!{Style.RESET_ALL}")
            break

        if wybor not in ['1', '2']:
            print(f"{Fore.RED}Błąd: Wybierz 1, 2 lub 0!{Style.RESET_ALL}")
            input("\nNaciśnij Enter, aby spróbować ponownie...")
            continue

        # Pobieranie danych wspólnych
        print(f"\n{Fore.BLUE}--- KONFIGURACJA ---{Style.RESET_ALL}")
        kod = input(f"{Fore.WHITE}Wpisz kod zabezpieczeń (ziarno): {Style.RESET_ALL}")

        if not kod:
            print(f"{Fore.RED}Błąd: Kod nie może być pusty!{Style.RESET_ALL}")
            input("\nNaciśnij Enter...")
            continue

        coder = WinterCoder(kod)

        if wybor == '1':
            tekst = input(f"{Fore.WHITE}Wpisz tekst do zakodowania: {Style.RESET_ALL}")
            zakodowane = coder.encode(tekst)
            print(f"\n{Fore.GREEN}✅ ZAKODOWANO POMYŚLNIE:{Style.RESET_ALL}")
            print(f"{Fore.BLACK}{Fore.LIGHTWHITE_EX}{zakodowane}{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Wskazówka: Skopiuj powyższy ciąg zer i jedynek.{Style.RESET_ALL}")

        elif wybor == '2':
            binarka = input(f"{Fore.WHITE}Wklej ciąg binarny do odkodowania: {Style.RESET_ALL}").strip()
            if not all(c in '01' for c in binarka):
                print(f"{Fore.RED}Błąd: Ciąg zawiera niedozwolone znaki (używaj tylko 0 i 1)!{Style.RESET_ALL}")

                # 2. Sprawdzenie długości (podzielność przez 7)
            elif len(binarka) % 7 != 0:
                dlugosc = len(binarka)
                brakujace = 7 - (dlugosc % 7)
                print(f"{Fore.RED}Błąd: Niepełny ciąg binarny!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Twoja wiadomość ma {Fore.CYAN}{dlugosc}{Fore.YELLOW} bitów.")
                print(f"{Fore.YELLOW}Brakuje jeszcze {brakujace}.{Style.RESET_ALL}")
                odkodowane = coder.decode(binarka)
                print(f"\n{Fore.CYAN}🔓 ODKODOWANA TREŚĆ:{Style.RESET_ALL}")
                print(f"{Fore.WHITE}{Style.BRIGHT}{odkodowane}{Style.RESET_ALL}")

            else:
                odkodowane = coder.decode(binarka)
                print(f"\n{Fore.CYAN}🔓 ODKODOWANA TREŚĆ:{Style.RESET_ALL}")
                print(f"{Fore.WHITE}{Style.BRIGHT}{odkodowane}{Style.RESET_ALL}")

        input(f"\n{Fore.RED}Naciśnij Enter, aby wrócić do menu... {Style.RESET_ALL}")


if __name__ == "__main__":
    main()