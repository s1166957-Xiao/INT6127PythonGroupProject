import sqlite3
import os
import pandas as pd
from datetime import datetime

class DatabaseManager:
    """数据库管理类"""
    def __init__(self, db_file='express.db'):
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        self.initialize_database()
    
    def connect(self):
        """建立数据库连接"""
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.cursor = None
        self.conn = None
    
    def initialize_database(self):
        """初始化数据库"""
        try:
            self.connect()
            
            # 创建用户表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL
                )
            ''')
            
            # 创建快递表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS express (
                    express_id TEXT PRIMARY KEY,
                    pick_code TEXT UNIQUE NOT NULL,
                    sender_id TEXT NOT NULL,
                    receiver_id TEXT NOT NULL,
                    location TEXT NOT NULL,
                    notes TEXT,
                    status TEXT NOT NULL,
                    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sender_id) REFERENCES users (id),
                    FOREIGN KEY (receiver_id) REFERENCES users (id)
                )
            ''')
            
            # 如果是新数据库，尝试从Excel导入数据
            self.migrate_from_excel()
            
            self.conn.commit()
            
        except Exception as e:
            print(f"初始化数据库出错: {str(e)}")
            if self.conn:
                self.conn.rollback()
        finally:
            self.disconnect()
    
    def migrate_from_excel(self):
        """从Excel文件迁移数据到数据库"""
        try:
            # 检查是否已有数据
            self.cursor.execute("SELECT COUNT(*) FROM users")
            if self.cursor.fetchone()[0] > 0:
                return  # 数据库已有数据，不需要迁移
            
            # 导入用户数据
            if os.path.exists('user.xlsx'):
                df_user = pd.read_excel('user.xlsx', engine='openpyxl')
                for _, row in df_user.iterrows():
                    self.cursor.execute(
                        "INSERT INTO users (id, name) VALUES (?, ?)",
                        (str(row[0]), str(row[1]))
                    )
            
            # 导入快递数据
            if os.path.exists('express.xlsx'):
                df_express = pd.read_excel('express.xlsx', engine='openpyxl')
                for _, row in df_express.iterrows():
                    self.cursor.execute('''
                        INSERT INTO express (
                            express_id, pick_code, sender_id, receiver_id,
                            location, notes, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        str(row[0]), str(row[1]), str(row[2]), str(row[3]),
                        str(row[4]), str(row[5]), str(row[6])
                    ))
            
            self.conn.commit()
            print("数据迁移完成")
            
        except Exception as e:
            print(f"数据迁移出错: {str(e)}")
            self.conn.rollback()
    
    def execute_query(self, query, parameters=None):
        """执行查询并返回结果"""
        try:
            self.connect()
            if parameters:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        finally:
            self.disconnect()
    
    def execute_update(self, query, parameters=None):
        """执行更新操作"""
        try:
            self.connect()
            if parameters:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"执行更新出错: {str(e)}")
            if self.conn:
                self.conn.rollback()
            return False
        finally:
            self.disconnect()
    
    # 用户相关操作
    def get_all_users(self):
        """获取所有用户"""
        return self.execute_query("SELECT * FROM users ORDER BY id")
    
    def add_user(self, user_id, name):
        """添加新用户"""
        return self.execute_update(
            "INSERT INTO users (id, name) VALUES (?, ?)",
            (user_id, name)
        )
    
    def update_user(self, user_id, name):
        """更新用户信息"""
        return self.execute_update(
            "UPDATE users SET name = ? WHERE id = ?",
            (name, user_id)
        )
    
    def delete_user(self, user_id):
        """删除用户"""
        return self.execute_update(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )
    
    # 快递相关操作
    def get_all_express(self):
        """获取所有快递"""
        return self.execute_query("""
            SELECT e.*, 
                   s.name as sender_name, 
                   r.name as receiver_name
            FROM express e
            JOIN users s ON e.sender_id = s.id
            JOIN users r ON e.receiver_id = r.id
            ORDER BY e.create_time DESC
        """)
    
    def add_express(self, express_id, pick_code, sender_id, receiver_id, 
                   location, notes, status="在库"):
        """添加新快递"""
        return self.execute_update("""
            INSERT INTO express (
                express_id, pick_code, sender_id, receiver_id,
                location, notes, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (express_id, pick_code, sender_id, receiver_id, 
              location, notes, status))
    
    def update_express_status(self, express_id, status):
        """更新快递状态"""
        return self.execute_update("""
            UPDATE express 
            SET status = ?, update_time = CURRENT_TIMESTAMP
            WHERE express_id = ?
        """, (status, express_id))
    
    def get_express_by_pick_code(self, pick_code):
        """通过取件码获取快递信息"""
        results = self.execute_query("""
            SELECT e.*, 
                   s.name as sender_name, 
                   r.name as receiver_name
            FROM express e
            JOIN users s ON e.sender_id = s.id
            JOIN users r ON e.receiver_id = r.id
            WHERE e.pick_code = ?
        """, (pick_code,))
        return results[0] if results else None
    
    def search_express(self, query):
        """搜索快递"""
        query = f"%{query}%"
        return self.execute_query("""
            SELECT e.*, 
                   s.name as sender_name, 
                   r.name as receiver_name
            FROM express e
            JOIN users s ON e.sender_id = s.id
            JOIN users r ON e.receiver_id = r.id
            WHERE e.express_id LIKE ?
               OR e.sender_id LIKE ?
               OR e.receiver_id LIKE ?
               OR s.name LIKE ?
               OR r.name LIKE ?
        """, (query, query, query, query, query))
    
    # 统计相关操作
    def get_express_stats(self):
        """获取快递统计信息"""
        stats = {}
        
        # 在库快递总数
        result = self.execute_query(
            "SELECT COUNT(*) FROM express WHERE status = '在库'"
        )
        stats['in_storage'] = result[0][0] if result else 0
        
        # 今日入库数量
        result = self.execute_query("""
            SELECT COUNT(*) FROM express 
            WHERE DATE(create_time) = DATE('now', 'localtime')
        """)
        stats['today_in'] = result[0][0] if result else 0
        
        # 今日取件数量
        result = self.execute_query("""
            SELECT COUNT(*) FROM express 
            WHERE DATE(update_time) = DATE('now', 'localtime')
            AND status = '已取件'
        """)
        stats['today_out'] = result[0][0] if result else 0
        
        # 位置分布情况
        result = self.execute_query("""
            SELECT location, COUNT(*) as count
            FROM express
            WHERE status = '在库'
            GROUP BY location
            ORDER BY count DESC
        """)
        stats['location_distribution'] = result if result else []
        
        return stats