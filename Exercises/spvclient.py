class SPVClient: 

    def __init__(self, blockheaders, keypairs):
        self.blockheaders = blockheaders #Blockheaders will the a list of all of the headers from the blocks in the block chain
        self.keypairs = keypairs #keypairs should be a dictionary of public keys as keys and private keys as values

    "Adds new header to the SPV client's list from the mining community"
    def add_new_header(self, header):
        self.blockheaders.append(header)
        return 'Header added successfully.'

    'How does the SPVclient get the block from the main node and then the transaction?'
     #need to change block to node later on

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

    def add_block(self, miner, block, proof, target_fork="main"):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.print(blockchain.coins)
        * The previous_hash referred in the block and the hash of a latest block
          in the chain match.
        Miners can choose which fork to add to. 
        If new_fork name is specified, create new fork based on existing targeted fork chain and index and add to new fork chain
        If no new fork_name is specified,
            block adds to the targeted chain. Default chain is the main chain.
        Index only matters for new fork creation
        If last 3 arguments not supplied, add block to main chain
        """

        selected_fork = self.chain 

        index = len(selected_fork) if index == None else index
        self.forked_chains[new_fork] = copy.copy(selected_fork[0:index+1])
        selected_chain = self.forked_chains[new_fork]

        previous_hash = self.last_block.hash

        if previous_hash != block.header["previous_hash"]:
            return False

        if not self.validate(block, proof):
            return False

        block.hash = proof
        selected_chain.append(block)

        self.add_transacted_coins(block, miner)
        self.release_locked_coins()
        
        return True
        

   