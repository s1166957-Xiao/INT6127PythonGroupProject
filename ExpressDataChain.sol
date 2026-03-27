// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title ExpressDataChain
 * @dev 快递管理系统数据上链合约
 * 用于存储快递信息和用户信息到区块链
 */
contract ExpressDataChain {
    
    // 事件定义
    event ExpressDataUploaded(uint256 indexed uploadId, uint256 timestamp, string dataHash);
    event UserDataUploaded(uint256 indexed uploadId, uint256 timestamp, string dataHash);
    event DataVerified(uint256 indexed uploadId, bool isValid);
    
    // 数据记录结构体
    struct DataRecord {
        uint256 uploadId;           // 上链记录ID
        address uploader;           // 上传者地址
        uint256 timestamp;          // 上链时间戳
        string dataHash;            // 数据哈希值（IPFS或SHA256）
        string dataType;            // 数据类型（"express" 或 "user"）
        uint256 recordCount;        // 记录数量
        bool isVerified;            // 是否已验证
    }
    
    // 状态变量
    mapping(uint256 => DataRecord) public dataRecords;  // 记录ID映射到记录
    mapping(address => uint256[]) public userUploadIds; // 用户的上链记录ID列表
    
    uint256 public totalUploads = 0;          // 总上链次数
    address public admin;                    // 管理员地址
    
    // 修饰符
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can call this function");
        _;
    }
    
    /**
     * @dev 合约初始化
     */
    constructor() {
        admin = msg.sender;
    }
    
    /**
     * @dev 上传快递数据
     * @param dataHash 数据哈希值（IPFS哈希或SHA256）
     * @param recordCount 快递记录数量
     * @return uploadId 返回上链记录ID
     */
    function uploadExpressData(string memory dataHash, uint256 recordCount) 
        public 
        returns (uint256) 
    {
        require(bytes(dataHash).length > 0, "Data hash cannot be empty");
        require(recordCount > 0, "Record count must be greater than 0");
        
        totalUploads++;
        uint256 uploadId = totalUploads;
        
        DataRecord memory record = DataRecord(
            uploadId,
            msg.sender,
            block.timestamp,
            dataHash,
            "express",
            recordCount,
            false
        );
        
        dataRecords[uploadId] = record;
        userUploadIds[msg.sender].push(uploadId);
        
        emit ExpressDataUploaded(uploadId, block.timestamp, dataHash);
        return uploadId;
    }
    
    /**
     * @dev 上传用户数据
     * @param dataHash 数据哈希值
     * @param recordCount 用户记录数量
     * @return uploadId 返回上链记录ID
     */
    function uploadUserData(string memory dataHash, uint256 recordCount) 
        public 
        returns (uint256) 
    {
        require(bytes(dataHash).length > 0, "Data hash cannot be empty");
        require(recordCount > 0, "Record count must be greater than 0");
        
        totalUploads++;
        uint256 uploadId = totalUploads;
        
        DataRecord memory record = DataRecord(
            uploadId,
            msg.sender,
            block.timestamp,
            dataHash,
            "user",
            recordCount,
            false
        );
        
        dataRecords[uploadId] = record;
        userUploadIds[msg.sender].push(uploadId);
        
        emit UserDataUploaded(uploadId, block.timestamp, dataHash);
        return uploadId;
    }
    
    /**
     * @dev 验证数据记录
     * @param uploadId 上链记录ID
     */
    function verifyDataRecord(uint256 uploadId) 
        public 
        onlyAdmin 
    {
        require(uploadId > 0 && uploadId <= totalUploads, "Invalid upload ID");
        require(!dataRecords[uploadId].isVerified, "Record already verified");
        
        dataRecords[uploadId].isVerified = true;
        emit DataVerified(uploadId, true);
    }
    
    /**
     * @dev 获取数据记录详情
     * @param uploadId 上链记录ID
     * @return 返回数据记录
     */
    function getDataRecord(uint256 uploadId) 
        public 
        view 
        returns (DataRecord memory) 
    {
        require(uploadId > 0 && uploadId <= totalUploads, "Invalid upload ID");
        return dataRecords[uploadId];
    }
    
    /**
     * @dev 获取用户的所有上链记录
     * @param userAddress 用户地址
     * @return 返回记录ID数组
     */
    function getUserUploadIds(address userAddress) 
        public 
        view 
        returns (uint256[] memory) 
    {
        return userUploadIds[userAddress];
    }
    
    /**
     * @dev 获取特定类型的最新记录
     * @param dataType 数据类型（"express" 或 "user"）
     * @return 返回最新记录
     */
    function getLatestRecordByType(string memory dataType) 
        public 
        view 
        returns (DataRecord memory) 
    {
        for (uint256 i = totalUploads; i > 0; i--) {
            if (keccak256(abi.encodePacked(dataRecords[i].dataType)) == 
                keccak256(abi.encodePacked(dataType))) {
                return dataRecords[i];
            }
        }
        revert("No record found for this data type");
    }
    
    /**
     * @dev 批量验证数据记录（仅管理员）
     * @param uploadIds 上链记录ID数组
     */
    function batchVerifyRecords(uint256[] memory uploadIds) 
        public 
        onlyAdmin 
    {
        for (uint256 i = 0; i < uploadIds.length; i++) {
            if (!dataRecords[uploadIds[i]].isVerified) {
                dataRecords[uploadIds[i]].isVerified = true;
                emit DataVerified(uploadIds[i], true);
            }
        }
    }
    
    /**
     * @dev 获取合约统计信息
     * @return 返回总上链次数
     */
    function getStatistics() 
        public 
        view 
        returns (uint256) 
    {
        return totalUploads;
    }
    
    /**
     * @dev 转移管理员权限（仅当前管理员）
     * @param newAdmin 新管理员地址
     */
    function transferAdmin(address newAdmin) 
        public 
        onlyAdmin 
    {
        require(newAdmin != address(0), "Invalid admin address");
        admin = newAdmin;
    }
}
