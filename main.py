from lexical.scanner import Scanner

def main():
    scanner = Scanner("source_code_test.mc")
    token = scanner.next_token()
    while token:
        print(token)
        token = scanner.next_token()
    print("Compilado com sucesso!")

if __name__ == "__main__":
    main()