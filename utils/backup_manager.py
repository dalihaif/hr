"""
数据备份恢复管理工具
支持数据库完整备份、压缩、恢复和清理
"""
import shutil
import gzip
import os
import datetime
import sqlite3


class BackupManager:
    """数据库备份管理器"""
    
    def __init__(self, db_path, backup_dir):
        """
        初始化备份管理器
        
        Args:
            db_path: 数据库文件路径
            backup_dir: 备份文件存储目录
        """
        self.db_path = db_path
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, backup_type='full'):
        """
        创建数据库备份
        
        Args:
            backup_type: 备份类型 ('full' 或 'incremental')
        
        Returns:
            备份文件路径
        """
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if backup_type == 'full':
            # 完整备份：复制并压缩数据库文件
            backup_filename = f'full_backup_{timestamp}.db.gz'
            backup_file = os.path.join(self.backup_dir, backup_filename)
            
            # 先验证数据库完整性
            if not self._verify_database():
                raise Exception("数据库验证失败，无法创建备份")
            
            # 压缩备份
            self._compress_file(self.db_path, backup_file)
            
            # 记录备份信息
            self._log_backup(backup_filename, 'full', os.path.getsize(backup_file))
            
            print(f"✓ 完整备份创建成功: {backup_filename}")
            return backup_file
        
        elif backup_type == 'incremental':
            # 增量备份（简化版：仅备份最近修改的数据）
            # TODO: 实现真正的增量备份逻辑
            backup_filename = f'incremental_backup_{timestamp}.sql.gz'
            backup_file = os.path.join(self.backup_dir, backup_filename)
            
            # 导出SQL
            self._export_sql(backup_file)
            
            print(f"✓ 增量备份创建成功: {backup_filename}")
            return backup_file
        
        else:
            raise ValueError(f"不支持的备份类型: {backup_type}")
    
    def restore_backup(self, backup_file):
        """
        恢复数据库备份
        
        Args:
            backup_file: 备份文件路径
        
        Returns:
            True表示恢复成功
        """
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"备份文件不存在: {backup_file}")
        
        # 先备份当前数据库（防止恢复失败）
        temp_backup = self.create_backup('full')
        
        try:
            if backup_file.endswith('.gz'):
                # 解压备份文件
                temp_db = backup_file.replace('.gz', '.tmp')
                self._decompress_file(backup_file, temp_db)
                
                # 验证解压后的数据库
                if not self._verify_database(temp_db):
                    raise Exception("备份文件损坏，无法恢复")
                
                # 替换当前数据库
                shutil.copy2(temp_db, self.db_path)
                os.remove(temp_db)
            else:
                # 直接复制
                shutil.copy2(backup_file, self.db_path)
            
            print(f"✓ 数据库恢复成功: {os.path.basename(backup_file)}")
            return True
            
        except Exception as e:
            # 恢复失败，回滚到临时备份
            print(f"✗ 恢复失败: {e}")
            print("正在回滚...")
            shutil.copy2(temp_backup, self.db_path)
            os.remove(temp_backup)
            raise
    
    def list_backups(self):
        """
        列出所有备份文件
        
        Returns:
            备份文件列表，包含文件名、大小、创建时间等信息
        """
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        for filename in os.listdir(self.backup_dir):
            if filename.endswith(('.db.gz', '.sql.gz')):
                filepath = os.path.join(self.backup_dir, filename)
                stat = os.stat(filepath)
                
                backup_info = {
                    'filename': filename,
                    'filepath': filepath,
                    'size': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'created_at': datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                    'type': 'full' if 'full' in filename else 'incremental',
                }
                
                backups.append(backup_info)
        
        # 按创建时间降序排序
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return backups
    
    def cleanup_old_backups(self, keep_days=30):
        """
        清理过期备份
        
        Args:
            keep_days: 保留天数
        
        Returns:
            删除的备份数量
        """
        deleted_count = 0
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=keep_days)
        
        backups = self.list_backups()
        
        for backup in backups:
            backup_date = datetime.datetime.strptime(backup['created_at'], '%Y-%m-%d %H:%M:%S')
            
            if backup_date < cutoff_date:
                try:
                    os.remove(backup['filepath'])
                    deleted_count += 1
                    print(f"已删除过期备份: {backup['filename']}")
                except Exception as e:
                    print(f"删除失败 {backup['filename']}: {e}")
        
        print(f"✓ 清理完成，共删除 {deleted_count} 个过期备份")
        return deleted_count
    
    def download_backup(self, filename):
        """
        获取备份文件用于下载
        
        Args:
            filename: 备份文件名
        
        Returns:
            备份文件路径
        """
        filepath = os.path.join(self.backup_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"备份文件不存在: {filename}")
        
        return filepath
    
    # ============================================================
    # 私有方法
    # ============================================================
    
    def _compress_file(self, source_path, dest_path):
        """压缩文件"""
        with open(source_path, 'rb') as f_in:
            with gzip.open(dest_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    def _decompress_file(self, source_path, dest_path):
        """解压文件"""
        with gzip.open(source_path, 'rb') as f_in:
            with open(dest_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    def _export_sql(self, output_path):
        """导出数据库为SQL"""
        conn = sqlite3.connect(self.db_path)
        
        with open(output_path.replace('.gz', '.sql'), 'w') as f:
            for line in conn.iterdump():
                f.write('%s\n' % line)
        
        conn.close()
        
        # 压缩SQL文件
        sql_path = output_path.replace('.gz', '.sql')
        self._compress_file(sql_path, output_path)
        os.remove(sql_path)
    
    def _verify_database(self, db_path=None):
        """验证数据库完整性"""
        path = db_path or self.db_path
        
        try:
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            conn.close()
            
            return result[0] == 'ok'
        except Exception:
            return False
    
    def _log_backup(self, filename, backup_type, size):
        """记录备份日志"""
        log_file = os.path.join(self.backup_dir, 'backup_log.txt')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{timestamp} | {backup_type} | {filename} | {size} bytes\n")


def test_backup_manager():
    """测试备份管理器"""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import Config
    
    manager = BackupManager(Config.DB_PATH, Config.BACKUP_DIR)
    
    # 创建备份
    print("\n=== 测试创建备份 ===")
    backup_file = manager.create_backup('full')
    
    # 列出备份
    print("\n=== 测试列出备份 ===")
    backups = manager.list_backups()
    for backup in backups:
        print(f"  - {backup['filename']} ({backup['size_mb']} MB, {backup['created_at']})")
    
    # 清理过期备份（保留7天）
    print("\n=== 测试清理过期备份 ===")
    manager.cleanup_old_backups(keep_days=7)
    
    print("\n✓ 备份管理器测试完成")


if __name__ == '__main__':
    test_backup_manager()
