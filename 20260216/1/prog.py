import sys, os
from zlib import decompress


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


def get_last_commit(path, branch):
    if branch not in get_branches(path):
        raise ValueError("Error. No such branch")

    path_branch = os.path.join(path, ".git", "refs", "heads", branch)
    with open(path_branch) as f:
        commit_hash = f.read().strip()
    
    path_commit = os.path.join(path, ".git", "objects", commit_hash[:2], commit_hash[2:])
    with open(path_commit, "rb") as f:
        commit = f.read()
    commit = decompress(commit)
    commit = commit[commit.index(b'\x00') + 1:]
    return commit.decode('utf-8')


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
        try:
            commit_last = get_last_commit(argv[1], argv[2])
            print(commit_last)
        except ValueError as error:
            print(error)
            exit(1)

    else:
        print("Error. Too many parameters were given")
        exit(1)

if __name__ == "__main__":
    main()