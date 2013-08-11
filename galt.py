#! /usr/bin/python
import codecs
import getopt
import itertools
import math
import os
import sys
import time
from pygit2 import Repository, Tree
from pygit2 import GIT_SORT_TIME, GIT_SORT_REVERSE

def find_changes(commit):
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
    print "walk commits"
    iters = []
    for commit in repo.walk(repo.head.target, GIT_SORT_TIME):
        #print time.asctime(time.localtime(commit.commit_time))
        iters.append(find_changes(commit))

    return itertools.chain.from_iterable(iters)

def reduce_and_weight(changes):
    print "reduce and weight"
    N = 0 # total number of developers
    authors = list()
    nf = dict() # number of developers that changed a file
    cfd = dict() # number of commits by developer to file
    for a, f in changes:
        if a not in authors:
            authors.append(a)
            N += 1

        if f in nf:
            if a not in nf[f]:
                nf[f].append(a)
        else:
            nf[f] = [a]

        if (a, f) in cfd:
            cfd[(a, f)] += 1
        else:
            cfd[(a, f)] = 1

    for a, f in cfd.keys():
        weight = cfd[(a, f)] * math.log(N/len(nf[f]))
        yield (a, f, weight)

def weights_to_adjlist(weights):
    print 'weights to adjlist'
    return weights

## Cosine Similarity Functions
# Thanks to amundo:
# https://gist.github.com/amundo/288282
def scalar(collection):
    total = 0
    for filename, weight in collection.items()
        total += weight * weight
    return sqrt(total)

def cos_similarity(A, B):
    total = 0
    for filename in A:
        if filename in B:
            total += A[filename] * B[filename]
    return float(total) / (scalar(A) * scalar(B))
##

def write_file(outputfile, adjlist):
    print 'write file'
    if (not os.path.isfile(outputfile)):
        f = codecs.open(outputfile, "w", "utf-8")
        for a, b, w in adjlist:
            f.write('\'' +a + '\',\'' + b + '\',' + str(w) +'\n')
        f.close()
    else:
        print "woops file existed"
        sys.exit(2)

def main(argv):
    repopath = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hr:o:", ["help", "rpath=","ofile="])
    except getopt.GetoptError:
        print 'galt.py -r <repopath> -o <outputfile>'
        sys.exit(2)
    if len(opts) == 0:
        print 'galt.py -r <repopath> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print 'galt.py -r <repopath> -o <outputfile>'
            sys.exit()
        elif opt in ("-r", "--rpath"):
            repopath = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
            if os.path.exists(outputfile):
                print 'cannot write to path'
                sys.exit(2)
    repo = Repository(repopath)
    changes = walk_commits(repo)
    weighted = reduce_and_weight(changes)
    adjlist = weights_to_adjlist(weighted)
    if outputfile != '':
       write_file(outputfile, adjlist)
    else:
        for c in weighted:
            print c

if __name__ == "__main__":
    main(sys.argv[1:])
