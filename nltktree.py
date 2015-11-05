import nltk
import copy
# This program is used to do everything I need to do with the nltk.

# Makes the nltk tree from a string passed to it.
def maketree(tree_string):
    t = nltk.ParentedTree.fromstring(tree_string)
    return t

def getroot(subtree):
    crt = subtree
    while crt.parent() != None:
        crt = crt.parent()
    return crt

# To test if subtree1 dominates subtree2, we go up the tree from subtree2 until we either reach:
# the root, in which case we return false; or subtree1, in which case we return true.
def dominates(t, subtree1, subtree2):
    # The root dominates everything.
    if subtree1 == t.root(): return True

    crt = subtree2
    try:
        while crt != t.root() and crt.parent() != None:
            if crt == subtree1:
                return True
            crt = crt.parent()
    except AttributeError:
        return False
    return False

# Implementing the notion of C-Command; it might help.
# If A dominates B or B dominates A, there is no c-command.
# If A's first branching parent dominates B, then we have c-command.
def ccommands(t, subtree1, subtree2):
    if dominates(t, subtree1, subtree2) or dominates(t, subtree2, subtree1): return False
    if subtree1 is subtree2: return False

    crt = subtree1
    while len(crt) == 1 or (len(crt) == 2 and hasadverb(crt)): # TODO: Changed it to get parent if there is only the word plus an adverb.
        crt = crt.parent()

    return dominates(t, crt, subtree2)

def hasadverb(subtree):
    for child in subtree:
        if not type(child) is str:
            if child.label() == 'RB':
                return True
    return False

def generatelocalstructurefromsubtree(t, subtree):
    SENTENCE_PHRASES = ['S', 'SBAR', 'SQ', 'SBARQ','SINV']

    crt = subtree
    while not crt is t and not crt.label() in SENTENCE_PHRASES:
        crt = crt.parent()

    return crt

def has_phrases_between_trees(subtree1, subtree2, phrases):
    crt_phrase = subtree2

    while crt_phrase != subtree1 and crt_phrase.parent() != None:
        crt_phrase = crt_phrase.parent()
        if crt_phrase.label() in phrases: return True
        elif 'PRD' in phrases and crt_phrase.label().endswith('PRD'): return True

    return False

# Goes through the tree and gets the tuple indexes for each word in the tree,
# thus excluding the positions of the pos tags and phrase markers.
# This allows us to map the words by index in their list to their location
# in the tree.
#
# i.e.
# t = maketree(word_list's_tree)
# word_tree_positions = getwordtreepositions(t)
# word_list[4] <==> word_tree_positions[3]
#
# IMPORTANT - if the word_list contains the word 'ROOT' it is not mapped to, so we subtract by 1.
def getwordtreepositions(t):
    tree_pos_list = []
    for pos in t.treepositions():
        if isinstance(t[pos],str):
            tree_pos_list.append(pos)

    return tree_pos_list

# This will allow us to use the trees that correspond to the words, i.e. (VBZ is) instead of just 'is'
def getsmallestsubtrees(t):
    return [subtree for subtree in t.subtrees(lambda t: t.height() == 2)]

def getsmallestsubtreepositions(t, subtree_list = None):
    subtree_positions = []
    if not subtree_list:
        for subtree in t.subtrees(lambda t: t.height() == 2):
            subtree_positions.append(subtree.treeposition())
    else:
        for subtree in subtree_list:
            subtree_positions.append(subtree.treeposition())
    return subtree_positions


def lowest_common_subtree(t, word_list):
    positions = getsmallestsubtreepositions(t)

    head_idx = 0
    head = word_list[head_idx]
    tree_words = t.leaves()
    for i in range(0,len(tree_words)):
        if tree_words[i] == head:
            head_idx = i

    subtree = t[positions[head_idx]]
    while subtree.parent() != None:
        broke = False
        for word in word_list:
            if not word in subtree.leaves():
                subtree = subtree.parent()
                broke = True
                break
        if broke: continue
        while subtree.label()!='VP' and len(subtree.parent().leaves()) == len(word_list):
            subtree = subtree.parent()
        return subtree
    return subtree

# This sequentially creates trees for all possible combinations of a VP and its children
def get_linear_phrase_combinations(t, phrase):
    vp_combos = []
    for position in phrase_positions_in_tree(t, phrase):
        vp_combos.append(t[position])

        vp = vp_combos[-1].copy(deep=True)
        vp_copy = vp.copy(deep=True)
        for child in reversed(vp):
            vp_copy.remove(child)
            if len(vp_copy):
                vp_combos.append(vp_copy.copy(deep=True))

    return vp_combos

def phrase_positions_in_tree(t, phrase):
    subtree_vp_positions = []

    compare = lambda t: t.label() == phrase
    if phrase == 'predicative':
        compare = lambda t: t.label().endswith('PRD')

    for subtree in t.subtrees(compare):
        subtree_vp_positions.append(subtree.treeposition())

    return subtree_vp_positions

def get_nearest_phrase(t, idx, phrases):
    positions = getsmallestsubtreepositions(t)
    try: crt_node = t[positions[idx-1]]
    except IndexError:
        print 'Fuck'
        return None

    while not crt_node.label() in phrases:

        if crt_node.parent() == None:
            return None

        crt_node = crt_node.parent()

    return crt_node

def get_nearest_vp(t, idx):
    positions = getsmallestsubtreepositions(t)
    crt_node = t[positions[idx-1]]

    while crt_node.label() != 'VP' and crt_node.label() != 'SINV': # TODO: maybe change this to just VP!

        if crt_node.parent() == None:
            print 'WARNING - NO VP IN THIS SENTENCE!'
            return crt_node

        crt_node = crt_node.parent()

    return crt_node

# def get_closest_constituent(t, word_list):
#     head_idx = 0
#     head = word_list[head_idx]
#     tree_words = t.leaves()
#     for i in range(0,len(tree_words)):
#         if tree_words[i] == head:
#             try:
#                 if tree_words[i+1] == word_list[1]:
#                     head_idx = i
#                     break
#             except IndexError:
#                 head_idx = i
#                 break
#
#     positions = getsmallestsubtreepositions(t)
#     crt_node = t[positions[head_idx-1]]
#
#     while not contain_eachother(crt_node.leaves(), word_list):
#         if crt_node.parent() == None:
#             return crt_node
#
#         crt_node = crt_node.parent()
#
#     return crt_node

def contain_eachother(lst, check_lst):
    if len(lst) < len(check_lst): return False
    for w in check_lst:
        if w not in lst:
            return False
    return True

# This is just to print the sentence.
def printfrompositions(t, tree_pos_list):
    for pos in tree_pos_list:
        print t[pos],
    print '\n'



