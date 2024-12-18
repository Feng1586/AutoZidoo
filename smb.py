import subprocess
import os
import shutil
import paramiko
import datetime

def check_smb_service(host):
    try:
        # 调用 smbclient 命令，尝试连接共享
        result = subprocess.run(
            ["smbclient", f"\\\\{host}\\Share", "-U", "root%88888888", "-c", "dir"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(str(datetime.datetime.now())+f"SMB service on {host} is available. Shares:\n{result.stdout}")
            return True
        else:
            print(str(datetime.datetime.now())+f"SMB service on {host} is not available. Error:\n{result.stderr}")
            return False
    except Exception as e:
        print(str(datetime.datetime.now())+f"Error checking SMB service: {e}")
        return False

def get_smb_share(host):
    try:
        # 获取共享资源
        result = subprocess.run(
            ["smbclient", f"\\\\{host}\\Share", "-U", "root%88888888", "-c", "dir"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.splitlines()  # 解析并返回共享资源列表
        else:
            print(str(datetime.datetime.now())+f"Error getting SMB shares: {result.stderr}")
            return False
    except Exception as e:
        print(str(datetime.datetime.now())+f"Error getting SMB shares: {e}")
        return False

# 检查目录是否已挂载
def is_mounted(directory):
    with open('/proc/mounts', 'r') as f:
        mounts = f.readlines()
        for line in mounts:
            if directory in line:
                return True
    return False

# 获取目录的磁盘空间使用情况
def get_disk_usage(directory):
    try:
        total, used, free = shutil.disk_usage(directory)
        return total, used, free
    except FileNotFoundError:
        print(str(datetime.datetime.now())+f"Directory {directory} does not exist.")
        return None, None, None

# 判断 CIFS 服务是否挂载正常
def check_cifs_mount(directory):
    # 检查是否已挂载
    if not is_mounted(directory):
        print(str(datetime.datetime.now())+f"{directory} is not mounted.")
        return False

    try:
        # 获取磁盘空间
        total, used, free = get_disk_usage(directory)
        if total is None:
            print(str(datetime.datetime.now())+f"Failed to retrieve disk usage for {directory}.")
            return False
    except Exception as e:
        print(str(datetime.datetime.now())+f"Error checking disk usage: {e}")
        return False  # 在异常时直接返回

    print(str(datetime.datetime.now())+f"Disk usage for {directory}:")
    print(str(datetime.datetime.now())+f"Total: {total // (2**30)} GB")
    print(str(datetime.datetime.now())+f"Used: {used // (2**30)} GB")
    print(str(datetime.datetime.now())+f"Free: {free // (2**30)} GB")
    
    # 你可以根据实际需求判断是否满足挂载要求（例如：检查空间是否合理）
    if used < 0:  # 假设如果已用空间超过 90%，认为挂载可能不正常
        print(str(datetime.datetime.now())+"Warning: High disk usage, check the mount.")
        return False
    
    return True

# 使用 SSH 执行宿主机上的命令
def restart_cifs_service():
    # 设置 SSH 连接信息
    host = "192.168.100.1"  # 替换为宿主机的 IP 地址
    username = "root"      # 替换为宿主机的用户名
    password = "password"        # 替换为宿主机的密码

    try:
        # 创建 SSH 客户端
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动添加未知主机的 SSH 密钥

        # 连接宿主机
        print(str(datetime.datetime.now())+f"Connecting to {host} via SSH...")
        client.connect(host, username=username, password=password)

        # 执行重启 CIFS 服务的命令
        command = "/etc/init.d/cifs restart"
        print(str(datetime.datetime.now())+f"Executing command: {command}")
        stdin, stdout, stderr = client.exec_command(command)

        # 获取命令的输出和错误信息
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            print(str(datetime.datetime.now())+f"Command Output: {output}")
        if error:
            print(str(datetime.datetime.now())+f"Command Error: {error}")
            return False

        # 检查命令是否成功执行
        if stderr.channel.recv_exit_status() == 0:
            print(str(datetime.datetime.now())+"CIFS service restarted successfully.")
        else:
            print(str(datetime.datetime.now())+f"Failed to restart CIFS service. Error: {error}")

    except Exception as e:
        print(str(datetime.datetime.now())+f"Error while connecting to {host}: {e}")
    finally:
        client.close()  # 关闭 SSH 连接
        
# 生成配置文件
def generate_config_file(file_path, server_ip, share_name):
    config_content = f"""
config cifs
        option workgroup 'WORKGROUP'
        option delay '5'
        option enabled '1'

config natshare
        option enabled '1'
        option smbver '2.0'
        option agm 'rw'
        option iocharset 'utf8'
        option server '{server_ip}'
        option users 'root'
        option pwd '88888888'
        option natpath '/mnt/zidoo'
        option name '{share_name}'
"""
    # 将内容写入配置文件
    with open(file_path, 'w') as f:
        f.write(config_content)
    print(str(datetime.datetime.now())+f"Configuration file written to {file_path}")
    
# 强制刷新挂载点缓存
def refresh_mount_cache(directory):
    print(str(datetime.datetime.now())+f"Refreshing mount cache for {directory}...")
    # 执行 ls 命令来刷新挂载点状态
    try:
        subprocess.run(['ls', directory], check=True)
    except subprocess.CalledProcessError as e:
        print(str(datetime.datetime.now())+f"Error while refreshing mount cache: {e}")