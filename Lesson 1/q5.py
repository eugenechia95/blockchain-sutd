from hashlib import sha256


class MerkleNode:
    """
    Stores the hash and the parent.
    """
    def __init__(self, hash):
        self.hash = hash
        self.parent = None

class MerkleTree:
    
    """
    Stores the leaves and the root hash of the tree.
    """
    def __init__(self, data_chunks):
        self.leaves = []

        for chunk in data_chunks:
            node = MerkleNode(self.compute_hash(chunk))
            self.leaves.append(node)

        self.root = self.build()

    def add(data_chunks):
        # Add entries to tree
        for chunk in data_chunks:
            node = MerkleNode(self.compute_hash(chunk))
            self.leaves.append(node)

        self.root = self.build()

    def build():
        # Build tree computing new root
        """
        Builds the Merkle tree from a list of leaves. In case of an odd number of leaves, the last leaf is duplicated.
        """
        num_leaves = len(self.leaves)
        if num_leaves == 1:
            return leaves[0]

        parents = []

        i = 0
        while i < num_leaves:
            left_child = self.leaves[i]
            if (i+1) < num_leaves:
                right_child = self.leaves[i + 1]
            else:
                right_child = left_child

            parents.append(self.create_parent(left_child, right_child))

            i += 2

        return self.build_merkle_tree(parents)

    def get_proof(...):
        # Get membership proof for entry
        # TODO: WHICH NODES ARE NEEDED TO PROVE
        ...

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

        print("Left child: {}, Right child: {}, Parent: {}".format(
            left_child.hash, right_child.hash, parent.hash))
        return parent

    
    @staticmethod
    def compute_hash(data):
        data = data.encode('utf-8')
        return sha256(data).hexdigest()

def verify_proof(entry, proof, root):
    # Verify the proof for the entry and given root. Returns boolean.
    ...
