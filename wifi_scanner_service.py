import socket
import nmap
import ipaddress
import os
from scapy.all import sendp, RadioTap, Dot11, Dot11Deauth, Ether, ARP, srp
from alerter import send_multichoice_sms,send_open_sms
from DB_Manager import log_incident

remebered_devices = set()  # To keep track of known devices

def get_local_ip():
    """Automatically get the local IP address."""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        # If you get 127.0.0.1, try a better method
        if local_ip.startswith("127."):
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
        return local_ip
    except Exception as e:
        print(f"Error getting local IP: {e}")
        return None

def scan_network(ip_range):
    """Scan the subnet for live hosts and open ports."""
    print(f"🔍 Scanning network range: {ip_range}")
    scanner = nmap.PortScanner()
    scanner.scan(hosts=ip_range, arguments='-sP')  # Ping scan

    devices = []
    for host in scanner.all_hosts():
        if scanner[host].state() == 'up':
            mac = scanner[host]['addresses'].get('mac', 'N/A')
            devices.append((host, mac))

    return devices

def scan_ports(ip):
    """Scan common ports on a single device."""
    scanner = nmap.PortScanner()
    scanner.scan(ip, arguments='-T4 -F')  # Fast scan of common ports
    ports = []
    if ip in scanner.all_hosts():
        for proto in scanner[ip].all_protocols():
            ports.extend(scanner[ip][proto].keys())
    return sorted(ports)

def local_wifi_scan(user):
    """Perform a local Wi-Fi scan."""
    initiAL_scan = False
    while True:
        local_ip = get_local_ip()
        if not local_ip:
            print("❌ Could not determine local IP.")
            return
        net = ipaddress.IPv4Network(local_ip + '/24', strict=False)
        ip_range = str(net)

        devices = scan_network(ip_range)
        if not devices:
            print("⚠️ No active devices found.")
            return

        print("\n📡 Active devices found:\n")
        for ip, mac in devices:
            print(f"🟢 IP: {ip} | MAC: {mac}")
            devices_info = {
                'IP': ip,
                'MAC': mac
            }
            ports = scan_ports(ip)
            devices_info['Open Ports'] = ports
            if not initiAL_scan:
                if ports not in [None, [], '']:
                    send_open_sms(devices_info)
                    log_incident(user['id'], "open port detected", f"Device {devices_info['IP']} with MAC {devices_info['MAC']} has open ports", devices_info['IP'], 2, str(devices_info['Open Ports']))
                    
                remebered_devices.add(tuple(devices_info.items()))
                print(f"  Open ports: {ports if ports else 'None'}\n")
                initiAL_scan = True
            else:
                if tuple(devices_info.items()) not in remebered_devices:
                    print(f"    New device detected: {devices_info['IP']} | Open ports: {ports if ports else 'None'}\n")
                    send_multichoice_sms(devices_info)
                    log_incident(user['id'], "new device detected", f"New device {devices_info['IP']} with MAC {devices_info['MAC']} detected", devices_info['IP'], 1, str(devices_info['Open Ports']))
                else:
                    print(f"Device already known: {devices_info['IP']} | Open ports: {ports if ports else 'None'}\n")
        print("🔄 Rescanning in 10 seconds...")
        os.sleep(15)

def permit_device(ip, mac):
    """Permit a device to be added to the known devices list."""
    device_info = {'IP': ip, 'MAC': mac}
    device_info['Open Ports'] = scan_ports(ip)
    remebered_devices.add(tuple(device_info.items()))
    print(f"✅ Device {ip} with MAC {mac} has been added to the known devices list. User confirmed")
    #Alert the user that the device has been added


def get_router_mac(gateway_ip="192.168.1.1"):
    pkt = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=gateway_ip)
    ans, _ = srp(pkt, timeout=2, verbose=0)
    for _, rcv in ans:
        return rcv[Ether].src  # MAC address of the router
    return None


def deny_device(ip, mac):
    """Deny a device from being added to the known devices list."""
    target_mac = mac     # Victim device
    gateway_mac = get_router_mac()
    if  gateway_mac is None:
        print("❌ Could not retrieve the router's MAC address. Denial failed.")
        return
    interface = "wlan0mon"           
    # Deauth packet to client from AP
    packet = RadioTap() / Dot11(addr1=target_mac, addr2=gateway_mac, addr3=gateway_mac) / Dot11Deauth(reason=7)
    sendp(packet, iface=interface, count=5, inter=0.1)
    print(f"❌ Device {ip} with MAC {mac} has been denied access. User confirmed")
    