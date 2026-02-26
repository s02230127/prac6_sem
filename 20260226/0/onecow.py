import cowsay, sys

def main():
    if len(sys.argv) != 3:
        print('error')
        exit(1)
    print(cowsay.cowsay(message=sys.argv[1], cow=sys.argv[2]))


if __name__ == '__main__':
    main()