pragma solidity ^0.4.21;

contract basicContract{
    uint256 public expiration = 2**256-1;
}

contract expiry{
    function calculateExpiry() public returns(uint) {
        return now + 24 hours;
    }
}

contract CoinFlip is basicContract {
    address public Alice;
    bytes32 public AliceCommitment;

    uint256 public betAmount;

    address public Bob;
    bool public BobChoice;
    
    mapping (address => uint256) public currentWinner;
    
    modifier validCancel() {
        require(msg.sender == Alice);
        require(Bob == 0);
        _;
    }

    //fallback function
    function createBet(bytes32 commitment) public payable {
        Alice = msg.sender;
        //committment is a hash of boolean value (bet) and a secret 32 bit nonce
        AliceCommitment = commitment;
        betAmount = msg.value;
    }

    //only cancel bet when there is no other player who has accepted the bet
    function cancelBet() public validCancel() {
        betAmount = 0;
        //transfers balance in contract back to sender
        msg.sender.transfer(address(this).balance);    
    }

    function takeBet(bool choice) public payable {
        require(Bob == 0);
        require(msg.value == betAmount);

        Bob = msg.sender;
        BobChoice = choice;

        expiry Expiry = expiry(this);
        expiration = Expiry.calculateExpiry();
    }

    //Player A reveals bet and sees if player B manages to win by selecting same choice as playerA
    function reveal(bool choice, uint256 nonce) public {
        require(Bob != 0);
        require(now < expiration);

        require(sha256(abi.encodePacked(choice, nonce)) == AliceCommitment);

        if (BobChoice == choice) {
            Bob.transfer(address(this).balance);
            currentWinner[Bob] += 1;
        } else {
            Alice.transfer(address(this).balance);
            currentWinner[Alice] += 1;
        }
    }

    function claimTimeout() public {
        require(now >= expiration);

        Bob.transfer(address(this).balance);
    }
}
