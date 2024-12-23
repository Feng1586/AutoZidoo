import socket
import time
import uuid
import psutil
import logs

DISCOVER_HOST = "239.39.3.9"  # 多播地址
DISCOVER_PORT = 18239  # 端口号
TIMEOUT = 5  # 超时时间，单位为秒
mStop = False  # 用来控制接收循环的标志

# 获取本机的 IP 地址（只获取已连接的接口）
def get_local_ip():
    addresses = psutil.net_if_addrs()  # 获取所有网络接口的地址信息
    stats = psutil.net_if_stats()  # 获取接口的状态信息

    if 'eth0' in addresses and stats['eth0'].isup:  # 判断 eth0 是否存在并已连接
        for addr in addresses['eth0']:
            if addr.family == socket.AF_INET:  # 只获取 IPv4 地址
                return addr.address
    return None

# 创建多播 socket
mDiscoverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
mDiscoverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 绑定到本地地址和端口
mDiscoverSocket.bind(('', DISCOVER_PORT))

# 设置 socket 超时时间
mDiscoverSocket.settimeout(TIMEOUT)

# 组播加入
mDiscoverAddress = socket.inet_aton(DISCOVER_HOST)
mDiscoverSocket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mDiscoverAddress + socket.inet_aton('0.0.0.0'))

# 通知组内的设备，发送一次信息
def delay_notify_join():
    try:
        device_uuid = str(uuid.uuid4())
        message = (
            "JOIN\r\n"
            "uuid: " + device_uuid + "\r\n" +
            "type: 2\r\n" +
            "host: " + DISCOVER_HOST + "\r\n" +
            "port: " + str(DISCOVER_PORT) + "\r\n" +
            "\r\n"
        ).encode('utf-8')
        
        # 发送到多播地址
        mDiscoverSocket.sendto(message, (DISCOVER_HOST, DISCOVER_PORT))
    except Exception as e:
        logs.output_logs(f"Error sending message: {e}")
        
def parse_device(data):
    try:
        # 假设设备信息是按照特定格式传输的，我们直接打印数据
        logs.output_logs(f"Device Info: {data.decode('utf-8')}")
    except Exception as e:
        logs.output_logs(f"Error parsing device data: {e}")

# 监听来自组内设备的消息，带超时机制
def get_zidoo_address(timeout=TIMEOUT):
    # 发送一次通知
    delay_notify_join()
    local_ip = get_local_ip()
    while True:
        try:
            # 读取数据包
            data, addr = mDiscoverSocket.recvfrom(512)
            logs.output_logs(f"Received message from {addr}")
            
            
            # 如果接收到的消息来自本机，则忽略
            if addr[0] == local_ip:
                logs.output_logs("Received message from self, ignore")
                logs.output_logs("--------------------------------------------------------")
                continue
            # 解析设备信息
            parse_device(data)
            return addr[0]
            # 解析设备信息
            # parse_device(data)
            
        except socket.timeout:
            # 超过超时时间仍未接收到数据包
            logs.output_logs(f"No response within {TIMEOUT} seconds.")
            return False  # 返回错误，超时
        
        except Exception as e:
            logs.output_logs(f"Error receiving message: {e}")
            time.sleep(1)  # 可加入延时，防止频繁出现错误