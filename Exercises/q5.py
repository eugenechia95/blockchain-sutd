from hashlib import sha256
from ecdsa import SigningKey, VerifyingKey, NIST384p
from q4 import *

class MerkleNode:
    """
    Stores the hash and the parent.
    """
    def __init__(self, hash):
        self.hash = hash
        self.parent = None
        self.left_child = None
        self.right_child = None

class MerkleTree:
    
    """
    Stores the leaves and the root hash of the tree.
    """
    def __init__(self, data_chunks):
        self.leaves = []
        self.parents = []

        for chunk in data_chunks:
            node = MerkleNode(self.compute_hash(chunk))
            self.leaves.append(node)

        self.root = self.build(self.leaves)

    def add(data_chunks):
        # Add entries to tree
        self.parents = []
        for chunk in data_chunks:
            node = MerkleNode(self.compute_hash(chunk))
            self.leaves.append(node)

        self.root = self.build(self.leaves)

    def build(self, nodes):
        # Build tree computing new root
        # Builds the Merkle tree from a list of leaves. In case of an odd number of leaves, the last leaf is duplicated.
        parents = []
        num_nodes = len(nodes)
        if num_nodes == 1:
            return nodes[0]

        i = 0
        while i < num_nodes:
            left_child = nodes[i]
            if (i+1) < num_nodes:
                right_child = nodes[i + 1]
            else:
                right_child = left_child
            new_parents = self.create_parent(left_child, right_child)
            parents.append(new_parents)
            self.parents.append(new_parents)

            i += 2

        return self.build(parents)

    def get_proof(self, index):
        # Get membership proof for entry; minimum number of nodes needed to find root
        leaf_node = self.leaves[index]
        proof = []
        current_node = leaf_node
        while current_node.parent != None:
            proof.append(self.get_other_child(current_node))
            current_node = current_node.parent
        return proof

    def get_other_child(self, node):
        parent_node = node.parent
        if parent_node.left_child == node:
            return parent_node.right_child
        else:
            return parent_node.left_child     

    def get_root():
        # Return the current root
        self.root

    def create_parent(self, left_child, right_child):
        """
        Creates the parent node from the children, and updates
        their parent field.
        """
        parent = MerkleNode(
            self.compute_hash(left_child.hash + right_child.hash))
        left_child.parent, right_child.parent = parent, parent
        
        parent.left_child = left_child
        parent.right_child = right_child

        # print("Left child: {}, Right child: {}, Parent: {}".format(
        #     left_child.hash, right_child.hash, parent.hash))
        return parent

    
    @staticmethod
    def compute_hash(data):
        data = bytes(data)
        return sha256(data).hexdigest()

    @staticmethod
    def verify_proof(entry, proof, root):
        # Verify the proof for the entry and given root. Returns boolean.
        current_computed = entry
        for i in proof:
            current_computed = MerkleTree.compute_hash(current_computed + i.hash) 
        return current_computed == root.hash


sk = SigningKey.generate(curve=NIST384p)
vk = sk.verifying_key
tx = Transaction(vk, vk, "5", "5")
data_chunks = [tx,tx,tx,tx]
mk = MerkleTree(data_chunks)
print(mk.leaves)
print(mk.parents)
print(mk.root)
proof = mk.get_proof(0)
print(proof)
entry = MerkleTree.compute_hash(tx)
verification_status = MerkleTree.verify_proof(entry, proof, mk.root)
print(verification_status)
