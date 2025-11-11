// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

/// @title 小型文件的简易存储方案
/// @notice 将文件字节存储于链上，包含文件名、上传者及时间戳。上传时触发事件。
/// @dev 现实使用成本较高，只作为演示。
contract FileStorage {
    struct File {
        address uploader;//地址
        uint256 timestamp;//时间戳
        bytes data;//原始字节数据
        bytes32 hash; // keccak256(data)
        uint256 size;//文件大小
    }

    mapping(string => File) private files;// 按文件名存储文件
    string[] private fileNames;// 所有文件名列表（可遍历）

    event FileUploaded(string indexed name, address indexed uploader, uint256 size, bytes32 hash, uint256 timestamp);

    /// @notice 上传文件（若文件名已存在则覆盖）
    /// @param name 文件名
    /// @param data 原始字节数据
    function uploadFile(string calldata name, bytes calldata data) external {
        require(bytes(name).length > 0, "File name required");
        // 需要限制大小
        bytes32 h = keccak256(data);

        bool exists = bytes(files[name].data).length != 0;
        files[name] = File({
            uploader: msg.sender,
            timestamp: block.timestamp,
            data: data,
            hash: h,
            size: data.length
        });

        if (!exists) {
            fileNames.push(name);
        }

        emit FileUploaded(name, msg.sender, data.length, h, block.timestamp);
    }

    /// @notice 返回指定文件名的文件元数据和数据
    /// @param name T文件名
    /// @return uploader 该文件的上传者地址
    /// @return timestamp 上传时间
    /// @return data 原始文件字节
    /// @return hash 文件字节的 keccak256 哈希值
    /// @return size 文件字节长度
    function getFile(string calldata name) external view returns (
        address uploader,
        uint256 timestamp,
        bytes memory data,
        bytes32 hash,
        uint256 size
    ) {
        File storage f = files[name];
        require(f.timestamp != 0, "File not found");
        return (f.uploader, f.timestamp, f.data, f.hash, f.size);
    }

    /// @notice 返回指定文件的 keccak256 哈希值（若未找到则返回零）
    function getFileHash(string calldata name) external view returns (bytes32) {
        return files[name].hash;
    }

    /// @notice 返回存储的文件数量
    function fileCount() external view returns (uint256) {
        return fileNames.length;
    }

    /// @notice 返回索引位置处的文件名（索引从0开始）
    function fileNameAt(uint256 index) external view returns (string memory) {
        require(index < fileNames.length, "Index out of range");
        return fileNames[index];
    }
}