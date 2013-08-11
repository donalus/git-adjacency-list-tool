from pygit2 import Repository
from pygit2 import GIT_SORT_TIME, GIT_SORT_REVERSE
from pygit2 import Tree

repo = Repository('/home/donal/git')

def iter_log():
	for commit in repo.walk(repo.head.target, GIT_SORT_TIME):
		if len(commit.parents) > 0:
			parent = commit.parents[0]
		for entry in commit.tree:
			if entry.name in parent.tree:
				prev_oid = parent.tree[entry.name].oid
				oid = commit.tree[entry.name].oid
				has_changed = (oid != prev_oid)
				if has_changed:
					yield commit.author.email, entry.name, entry.filemode
			
			

changes = iter_log()
for c in changes:
	print c
