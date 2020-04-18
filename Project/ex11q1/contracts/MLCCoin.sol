pragma solidity ^0.4.21;

// ----------------------------------------------------------------------------
// ERC Token Standard #20 Interface
//
// ----------------------------------------------------------------------------
contract ERC20Interface {
    function totalSupply() public view returns (uint);
    function balanceOf(address _owner) public view returns (uint balance);
    function allowance(address _owner, address _spender) public view returns (uint256);
    function transfer(address _to, uint tokens) public returns (bool);
    function approve(address _spender, uint tokens) public returns (bool);
    function transferFrom(address _from, address _to, uint tokens) public returns (bool);

    event Transfer(address indexed _from, address indexed _to, uint tokens);
    event Approval(address indexed _owner, address indexed _spender, uint tokens);
}

// ----------------------------------------------------------------------------
// Safe Math Library 
// ----------------------------------------------------------------------------
contract SafeMath {
    function safeAdd(uint a, uint b) public pure returns (uint c) {
        c = a + b;
        require(c >= a);
    }
    function safeSub(uint a, uint b) public pure returns (uint c) {
        require(b <= a); c = a - b; } function safeMul(uint a, uint b) public pure returns (uint c) { c = a * b; require(a == 0 || c / a == b); } function safeDiv(uint a, uint b) public pure returns (uint c) { require(b > 0);
        c = a / b;
    }
}

contract MLCCoin is ERC20Interface, SafeMath {
    string public name;
    string public symbol;
    uint8 public decimals;
    
    uint256 public _totalSupply;
    
    mapping(address => uint256) _balances;
    mapping(address => mapping(address => uint256)) _allowed;
    
    constructor() public {
        name = "MLCCoin";
        symbol = "MLC";
        decimals = 3;
        _totalSupply = 1000000000;

        
        _balances[msg.sender] = _totalSupply;
        emit Transfer(address(0), msg.sender, _totalSupply);
    }
    
    function totalSupply() public view returns (uint256) {
        return _totalSupply;
    }
    
    function balanceOf(address _owner) public view returns (uint balance256) {
        return _balances[_owner];
    }
    
    function allowance(address _owner, address _spender) public view returns (uint256) {
        return _allowed[_owner][_spender];
    }
    
    function approve(address _spender, uint tokens) public returns (bool) {
        _allowed[msg.sender][_spender] = tokens;
        emit Approval(msg.sender, _spender, tokens);
        return true;
    }
    
    function transfer(address _to, uint tokens) public returns (bool) {
        _balances[msg.sender] = safeSub(_balances[msg.sender], tokens);
        _balances[_to] = safeAdd(_balances[_to], tokens);
        emit Transfer(msg.sender, _to, tokens);
        return true;
    }
    
    function transferFrom(address _from, address _to, uint tokens) public returns (bool) {
        _balances[_from] = safeSub(_balances[_from], tokens);
        _balances[_to] = safeAdd(_balances[_to], tokens);
        _allowed[_from][msg.sender] = safeSub(_allowed[_from][msg.sender], tokens);
        emit Transfer(_from, _to, tokens);
        return true;
    }
}
