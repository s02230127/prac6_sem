import sys, os

def get_branches(path):
    if not os.path.exists(path):
        raise ValueError("Error. Path does not exist")
    
    if not os.path.isdir(path):
        raise ValueError("Error. Path not a directory")

    path = os.path.join(path, ".git")
    if not os.path.isdir(path):
        raise ValueError("Error. Not a git repository")
    path = os.path.join(path, "refs", "heads")
    items = os.listdir(path)
    return items


def main():
    argv = sys.argv
    if len(argv) == 1:
        print("Error. No parameters were given")
        exit(1)
    elif len(argv) == 2:
        try:
            items = get_branches(argv[1])
            for i in items:
                print(i)
        except ValueError as error:
            print(error)
            exit(1)
    elif len(argv) == 3:
        pass
    else:
        print("Error. Too many parameters were given")
        exit(1)

if __name__ == "__main__":
    main()