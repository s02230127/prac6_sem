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
    items = []
    for root, dirs, files in os.walk(path):
        for f in files:
            items.append(os.path.relpath(os.path.join(root, f), path))
    return items


def get_last_commit_hash(path, branch):
    if branch not in get_branches(path):
        raise ValueError("Error. No such branch")

    path_branch = os.path.join(path, ".git", "refs", "heads", branch)
    with open(path_branch) as f:
        commit_hash = f.read().strip()
    return commit_hash


def get_commit(path, commit_hash):
    path_commit = os.path.join(path, ".git", "objects", commit_hash[:2], commit_hash[2:])
    with open(path_commit, "rb") as f:
        commit = f.read()
    commit = decompress(commit)
    commit = commit[commit.index(b'\x00') + 1:]
    return commit.decode('utf-8')


def tree_parser(tree):
    tree = tree[tree.index(b'\x00') + 1:]
    ind = 0
    tree_list = []
    while ind < len(tree):
        mode = tree[ind:tree.index(b' ', ind)]
        if mode == b'40000':
            mode = 'tree'
        else: 
            mode = 'blob'

        name = tree[tree.index(b' ', ind) + 1: tree.index(b'\x00', ind)]
        name = name.decode('utf-8')
        ind = tree.index(b'\x00', ind) + 1
        obj_hash = tree[ind:ind + 20].hex()
        ind += 20
        tree_list.append(mode + ' ' + obj_hash + '    ' + name)
    return tree_list
    

def get_tree(path, commit):
    commit = commit.split('\n')
    tree_hash = None
    for line in commit:
        line = line.split()
        if line and line[0] == "tree":
            tree_hash = line[1]
            break
    if tree_hash is None:
        raise ValueError('Error. No tree in commit')
    path_tree = os.path.join(path, ".git", "objects", tree_hash[:2], tree_hash[2:])
    with open(path_tree, "rb") as f:
        tree = f.read()
    
    tree = decompress(tree)
    tree = tree_parser(tree)
    return tree


def get_parent_commit_hash(commit):
    commit = commit.split('\n')
    for line in commit:
        line = line.split()
        if line and line[0] == "parent":
            return line[1]
    return None


def print_commit_history(path, branch):
    commit_hash = get_last_commit_hash(path, branch)
    while True:
        print(f"TREE for commit {commit_hash}")
        commit = get_commit(path, commit_hash)
        tree = get_tree(path, commit)
        for i in tree:
            print(i)
        
        commit_hash = get_parent_commit_hash(commit)
        if commit_hash is None:
            break


def main():
    argv = sys.argv
    if len(argv) == 1:
        print("Error. No parameters were given")
        exit(1)
    elif len(argv) == 2:
        try:
            #commit 1
            items = get_branches(argv[1])
            for i in items:
                print(i)
        except ValueError as error:
            print(error)
            exit(1)
    elif len(argv) == 3:
        try:
            
            #commit 2
            commit_hash = get_last_commit_hash(argv[1], argv[2])
            commit_last = get_commit(argv[1], commit_hash)
            print(commit_last)
            
            tree = get_tree(argv[1], commit_last)
            for i in tree:
                print(i)
            print()
            
            #commit 4
            print_commit_history(argv[1], argv[2])
        except ValueError as error:
            print(error)
            exit(1)

    else:
        print("Error. Too many parameters were given")
        exit(1)

if __name__ == "__main__":
    main()
