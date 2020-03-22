class SPVClient: 

    def __init__(self, blockheaders, public_key, private_key):
        self.blockheaders = blockheaders #Blockheaders will a list of all of the headers from the blocks in the block chain
        self.public_key = public_key
        self.private_key = private_key

    "Adds new header to the SPV client's list from the mining community"
    def add_new_header(self, header):
        self.blockheaders.append(header)
        return 'Header added successfully.'

    def verify_proof(self,transaction, proof, root):
        # Verify the proof for the entry and given root. Returns boolean.
        current_computed = transaction
        flag = False
        for j in range(len(self.blockheaders)):
            for i in proof:
                current_computed = MerkleTree.compute_hash(current_computed + i.hash) 
                flag = current_computed == root.hash
                if flag == True:
                    return flag
                else:
                    return 'Transaction not found.'
   