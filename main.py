import zidoo
import smb
import time
import file
import docker_c
import logs


zidoo_ip_address = zidoo.get_zidoo_address()
directory = "/mnt/zidoo"
config_file_path = "/app/etc/config/cifs"

if __name__ == "__main__":
    while True:
        time.sleep(30)
        
        zidoo_ip_address = zidoo.get_zidoo_address()
        # 如果返回值是False则表示没有获取到内网芝杜的IP地址，则尝试获取
        if zidoo_ip_address == False:
            logs.output_logs("Error getting Zidoo IP address.")
            logs.output_logs("没有获取到局域网内的芝杜IP地址，正在尝试重新获取")
            continue
        
        logs.output_logs("芝杜的IP地址为：" + zidoo_ip_address)
        
        time.sleep(1)
        
        # 检查芝杜播放器的SMB服务是否正常启动
        if smb.check_smb_service(zidoo_ip_address) == False:
            print("SMB service is not available.")
            continue
        
        logs.output_logs("芝杜播放器的SMB服务正常开启")
        
        time.sleep(1)
        
        # 获取SMB Share
        share_files = smb.get_smb_share(zidoo_ip_address)
        if share_files == False:
            logs.output_logs("Error getting SMB share.")
            continue
        
        # 处理share_files列表
        share_files = [line.strip().split()[0].strip() for line in share_files if line.strip() and not line.startswith('\t')]
        # 只保留 Storage 和 D9E3-B639
        share_files = [name for name in share_files if name not in ['.', '..'] and name]
        print(share_files)
        
        # 去除文件列表中的 Storage
        share_files.remove("Storage")
        
        # 如果去除Storage后文件列表为空，则继续循环
        if len(share_files) == 0:
            print("No files available.")
            continue
        
        time.sleep(1)
        
        # 检查挂载情况
        if smb.check_cifs_mount(directory):
            logs.output_logs(f"{directory} is mounted and operational.")
        else:
            logs.output_logs(f"{directory} is not properly mounted.")
            logs.output_logs("正在重新生成配置文件")
            time.sleep(1)
            # 生成配置文件
            smb.generate_config_file(config_file_path, zidoo_ip_address, "Share/"+share_files[0])
            
            logs.output_logs("正在重启相关文件挂载服务器")
            time.sleep(1)
            # 重启 CIFS 服务
            flag = smb.restart_cifs_service()
            if flag == False:
                logs.output_logs("CIFS 挂载 芝杜SMB失败，30秒后重试")
                continue
            logs.output_logs("正在刷新挂载缓存")
            time.sleep(1)
            # 刷新挂载缓存
            smb.refresh_mount_cache("/mnt/zidoo")
            time.sleep(1)
            # 检查相关路径文件，如果没有则创建
            logs.output_logs("正在检查相关路径文件")
            file.create_media_structure()
            time.sleep(1)
            # 重启受到影响的容器
            logs.output_logs("正在重启受到影响的容器")
            docker_c.restart_qbittorret()
            time.sleep(1)
            continue
        
        time.sleep(1)
        # 检查相关路径，如果没有则创建
        file.create_media_structure()
        
        # 检查qbittorrent容器是否正常运行
        time.sleep(1)
        docker_c.check_qbittorrent()
            
        
            
            
            
            
            