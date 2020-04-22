pragma solidity ^0.4.21;

contract basicContract{
    uint256 public expiration = 2**256-1;
}

contract CoinFlip is basicContract {
    address public Alice;
    bytes32 public AliceCommitment;

    uint256 public betAmount;

    address public Bob;
    bool public BobChoice;

    string public betStatus = "No Bet Yet";
    
    address public currentWinner;
    
    modifier validCancel() {
        require(msg.sender == Alice);
        require(Bob == 0);
        _;
    }

    //fallback function
    function createBet(bool choice, uint256 nonce) public payable {
        Alice = msg.sender;
        //committment is a hash of boolean value (bet) and a secret 32 bit nonce
        AliceCommitment = sha256(abi.encodePacked(choice, nonce));
        betAmount = msg.value;
        betStatus = "Bet Not Accepted Yet";
    }

    //only cancel bet when there is no other player who has accepted the bet
    function cancelBet() public validCancel() {
        betAmount = 0;
        //transfers balance in contract back to sender
        msg.sender.transfer(address(this).balance);    
        betStatus = "Bet Cancelled";
    }

    function takeBet(bool choice) public payable {
        require(Bob == 0, "not zero");
        require(msg.value == betAmount, "not correct value");

        Bob = msg.sender;
        BobChoice = choice;

        betStatus = "Bet Accepted";

        expiration = now + 24 hours;
    }

    //Alice reveals bet and sees if Bob manages to win by selecting same choice as playerA
    function reveal(bool choice, uint256 nonce) public {
        require(msg.sender == Alice);
        require(Bob != 0);
        require(now < expiration);

        require(sha256(abi.encodePacked(choice, nonce)) == AliceCommitment);

        if (BobChoice == choice) {
            Bob.transfer(address(this).balance);
            currentWinner = Bob;
        } else {
            Alice.transfer(address(this).balance);
            currentWinner = Alice;
        }
        betStatus = "Bet Concluded";
    }

    function claimTimeout() public {
        require(msg.sender == Bob);
        require(now >= expiration);

        Bob.transfer(address(this).balance);

        betStatus = "Bet Expired";
    }

    function getBet() view public returns(uint256){
        return(betAmount);
    }

    function getStatus() view public returns(string){
        return(betStatus);
    }

    function getWinner() view public returns(address){
        return(currentWinner);
    }
}
