pragma solidity ^0.4.10;

// contract Auction {
    
//     address winner;
//     uint lastBid;
    
//     function Auction() public {
//         winner = msg.sender;
//         lastBid = 0;
//     }

//     function bid() public payable {
//         assert(msg.value > lastBid);
//         if (lastBid > 0) {
//             assert(winner.call.value(lastBid)());
//         }
//         winner = msg.sender;
//         lastBid = msg.value;
//     }
    
//     function getWinner() public returns(address) {
//         return winner;
//     }
    
// }

// // fixed code
contract Auction {
    
    address winner;
    uint lastBid;
    address failedRecipient;
    uint failedBid;
    
    function Auction() public {
        winner = msg.sender;
        lastBid = 0;
    }

    function bid() public payable {
        assert(msg.value > lastBid);
        if (lastBid > 0) {
            bool success = winner.send(lastBid);
            if (!success) {
                failedRecipient = winner;
                failedBid = lastBid;
            }
        }
        winner = msg.sender;
        lastBid = msg.value;
    }
    
    function getWinner() public returns(address) {
        return winner;
    }
    
    function getfailedRecipient() public returns(address) {
        return failedRecipient;
    }
    
    function getfailedBid() public returns(uint) {
        return failedBid;
    }
    
    function getBalance() public returns(uint) {
        return(this.balance);
    }
    
}

//Can deny any new bidders
contract Attack {

  Auction attacked;

  function Attack(address victim) public{
    attacked = Auction(victim);
  }

  function() public payable {
    revert();
  }
  
  function deposit() public payable{
  }

  function transfer() public{
    attacked.bid.value(address(this).balance)();
  }
  
  function getBalance() public returns(uint) {
        return(this.balance);
    }

}
