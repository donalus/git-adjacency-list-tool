#! /usr/bin/python
from pygit2 import Repository
from pygit2 import Tree
from pygit2 import GIT_SORT_TIME, GIT_SORT_REVERSE

def find_changes(commit):
    if len(commit.parents) > 0:
        for parent in commit.parents:
            for entry in commit.tree:
                if entry.name in parent.tree:
                    prev_oid = parent.tree[entry.name].oid
                    oid = commit.tree[entry.name].oid
                    has_changed = (oid != prev_oid)
                    if has_changed:
                        yield commit.author.email, entry.name, entry.filemode
                else:
                    yield commit.author.email, entry.name, entry.filemode
    else:
        for entry in commit.tree:
            yield commit.author.email, entry.name, entry.filemode

def find_changes2(commit):
    ct = commit.tree
    if len(commit.parents) > 0:
        for parent in commit.parents:
            pt = parent.tree
            diff = pt.diff_to_tree(ct)
            for patch in diff:
                yield commit.author.email, patch.new_file_path
    else:
        diff = ct.diff_to_tree()
        for patch in diff:
            yield commit.author.email, patch.new_file_path

def walk_commits(repo):
    for commit in repo.walk(repo.head.target, GIT_SORT_TIME):
        changes = find_changes(commit)
        for c in changes:
            print c
    return changes

def main():
    repo = Repository('/home/donal/gittest')
    changes = walk_commits(repo)

if __name__ == "__main__":
    main()
