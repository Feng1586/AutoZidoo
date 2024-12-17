import docker
import time

#重启qbittorrent容器

def restart_qbittorret():
    # 创建Docker客户端
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    
    # 列出所有容器
    containers = client.containers.list(all=True)
    for container in containers:
        print(f"Container {container.id}: {container.name}")
        
    container_id = "qbittorrent"
    container = client.containers.get(container_id)
    try:
        container.stop(timeout=30)
    except Exception as e:
        print(f"Error stopping container {container.id}: {e}")
        return False
    time.sleep(10)
    try:
        container.start()
    except Exception as e:
        print(f"Error starting container {container.id}: {e}")
        return False
    print(f"Container {container.id} restarted.")

def check_qbittorrent():
    # 创建Docker客户端
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    
    # 列出所有容器
    containers = client.containers.list(all=True)
    for container in containers:
        print(f"Container {container.id}: {container.name}")
        
    container_id = "qbittorrent"
    container = client.containers.get(container_id)
    print(f"Container {container.id}: {container.name}")
    
    if container.status == "running":
        print(f"Container {container.id} is running.")
        return True
    else:
        print(f"Container {container.id} is not running.")
        # 如果容器没有启动则尝试启动容器
        try:
            container.start()
        except Exception as e:
            print(f"Error starting container {container.id}: {e}")
            return False