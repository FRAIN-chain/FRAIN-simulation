// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;

contract CommitReveal {
    uint256 public round;
    mapping(uint256 => mapping(address => bytes32)) public saved_commits; // round => address => values

    mapping(uint256 => mapping(address => bytes)) public revealed_value;
    mapping(uint256 => mapping(address => bytes32))
        public revealed_hashed_value;

    function commit_hashed(
        bytes32 res, // hash of result
        // address addr, // address
        uint256 seed, // random value
        uint256 r // round
    ) external returns (bytes32) {
        address _msgSender = msg.sender;
        bytes32 value = keccak256(abi.encodePacked(res, _msgSender, seed));

        require(
            saved_commits[r][_msgSender] == 0,
            "CommitReveal::commit_hashed: Not-empty."
        );

        saved_commits[r][_msgSender] = value;

        return value;
    }

    function reveal_hashed(
        bytes32 res, // hash of result
        address addr, // address
        uint256 seed, // random value
        uint256 r // round
    ) external returns (bool) {
        bytes32 restored_value = keccak256(abi.encodePacked(res, addr, seed));

        require(
            saved_commits[r][addr] == restored_value,
            "CommitReveal::reveal: Reveal Failed."
        );

        revealed_hashed_value[r][addr] = res;

        return true;
    }

    function commit(
        bytes calldata res, // result
        // address addr, // address
        uint256 seed, // random value
        uint256 r // round
    ) external returns (bytes32) {
        address _msgSender = msg.sender;
        bytes32 value = keccak256(abi.encodePacked(res, _msgSender, seed));

        require(
            saved_commits[r][_msgSender] == 0,
            "CommitReveal::commit: Not-empty."
        );

        saved_commits[r][_msgSender] = value;

        return value;
    }

    function reveal(
        bytes calldata res, // result
        address addr, // address
        uint256 seed, // random value
        uint256 r // round
    ) external returns (bool) {
        bytes32 restored_value = keccak256(abi.encodePacked(res, addr, seed));

        require(
            saved_commits[r][addr] == restored_value,
            "CommitReveal::reveal: Reveal Failed."
        );

        revealed_value[r][addr] = res;

        return true;
    }

    // Utils

    function hashString(string memory input) external pure returns (bytes32) {
        return keccak256(abi.encodePacked(input));
    }

    function stringToBytes(
        string memory input
    ) external pure returns (bytes memory) {
        return abi.encodePacked(input);
    }

    function bytesToString(
        bytes memory input
    ) external pure returns (string memory) {
        return string(input);
    }
}
