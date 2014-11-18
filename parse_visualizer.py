"""
Allows to visualize the discourse trees in the training set.
"""

import networkx as nx
import matplotlib.pyplot as plt

filepath = '/Users/koopuluri/Downloads/train_data/file2.dis'

with open(filepath, 'r') as f:
    text = ''.join([''.join(line.split()) for line in f.readlines()])


class Node:
    def __init__(self, val):
        self.val = val
        self.children = []


def recurse(str, i):
    string = ''
    subtree = Node('')
    while True:
        if str[i] == '(':
            child_node, i = recurse(str, i+1)
            subtree.children.append(child_node)
        elif str[i] == ')':
            subtree.val = string
            return subtree, i
        else:
            string += str[i]
        i += 1
        if i == len(str):
            print 'POOP'
            return None

out, last = recurse(text, 1)

def visualize_tree(root):
    G = nx.Graph()
    depth = 0
    G.add_node(root.val+'0')
    struct = [root]
    max_size = 0
    while struct:
        node = struct.pop()
        node.val += str(depth)
        if len(node.children) > max_size:
            max_size = len(node.children)
        for c in node.children:
            G.add_node(c.val)
            G.add_edge(node.val, c.val)
            struct.insert(0, c)
    print 'about to draw!'
    nx.draw(G, with_labels=True)
    import pdb; pdb.set_trace()
    plt.show()

visualize_tree(out)

