pragma solidity ^0.4.24;

contract Transaction {

    address private owner;

    struct Shipment {
        address receiver;
        address sender;
        bytes32 shipmentHash;
        uint256 amount;
        bool status;
    }

    mapping(uint => Shipment) private shipments;

    uint private shipmentsCount;

    constructor() public {
        owner = msg.sender;
    }

    function sendShipment(address _receiver, bytes32 _shipmentHash, uint256 _amount) public {
        if (shipmentsCount != 0){
            require(shipments[shipmentsCount].status == true, "Shipment still in transit");
            require(msg.sender == shipments[shipmentsCount].receiver, "You do not possess the shipment");
        }
        else{
            require(msg.sender == owner, "You do not possess the shipment");
        }
        shipmentsCount ++;
        shipments[shipmentsCount] = Shipment(_receiver, msg.sender, _shipmentHash, _amount, false);
    }

    function receiveShipment(bytes32 _shipmentHash) public payable {
        require(_shipmentHash == shipments[shipmentsCount].shipmentHash, "Wrong Shipment Hash!");
        require(msg.value/1e18 == shipments[shipmentsCount].amount, "Wrong payment amount");
        require(msg.sender == shipments[shipmentsCount].receiver, "You are not the correct receipient!");

        shipments[shipmentsCount].status = true;
        shipments[shipmentsCount].sender.transfer(msg.value);
    }

    function getShipmentsCount() public view returns(uint) {
        return(shipmentsCount);
    }

    function getOwner() public view returns(address) {
        return(owner);
    }

    function getCurrentOwner() public view returns(address) {
        if (shipmentsCount != 0){
            if (shipments[shipmentsCount].status == true){
                return(shipments[shipmentsCount].receiver);
            }
            else{
                //Client app will process this result as "Still in Transit"
                return(address(0));
            }
        }
        else{
            return(owner);
        }
    }

    //Contract owner can destroy the contract if no shipments have been sent out yet.
    function shutdown() public {
        require(msg.sender == owner, "You are not the contract owner!");
        require(shipmentsCount == 0, "Shipments already sent out");
        selfdestruct(msg.sender);
    }

    /** Get Individual Shipment Details */

    function getShipmentReceiver(uint count) public view returns(address) {
        return(shipments[count].receiver);
    }

    function getShipmentSender(uint count) public view returns(address) {
        return(shipments[count].sender);
    }

    function getShipmentAmount(uint count) public view returns(uint256) {
        return(shipments[count].amount);
    }

    function getShipmentStatus(uint count) public view returns(bool) {
        return(shipments[count].status);
    }
}
