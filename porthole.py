import ipaddress
import socket
import time
import argparse


def process_cidr_input():
    """Processes the CIDR notation a uuser gave to make sure it is valid."""
    while True:
        cidr_input = input("Enter your CIDR notation: ")
        try:
            network = ipaddress.ip_network(cidr_input)
            return network
        except ValueError as e:
            print(f"Invalid CIDR: {e}")
            print("Try again.\n")
            
def parse_ports(port_input):
    """Parses port formats """
    ports = set()

    for part in port_input.split(","):
        if "-" in part:
            start, end = map(int, part.split("-"))
            ports.update(range(start, end + 1))
        else:
            ports.add(int(part))

    return sorted(ports)

def scan_port(ip, port):
    """Checks if specific port is open"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((str(ip), port))
            return result == 0
    except:
        return False

def scan_host(ip, port=80):
    """Shows how long the response/request took converting the time to miliseconds, and shows if the network is becoming smaller or larger (up or down)."""
    start_time = time.time()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((str(ip), port))

        duration = (time.time() - start_time) * 1000
        return "UP", f"{duration:.2f} ms"

    except socket.timeout:
        duration = (time.time() - start_time) * 1000
        return "DOWN", f"{duration:.2f} ms"

    except socket.error as e:
        duration = (time.time() - start_time) * 1000
        return "ERROR", f"{duration:.2f} ms"


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="IP Scanner")
    parser.add_argument("-p", "--ports", required=True, help="Ports to scan (80, 1-100, 80,443)")
    parser.add_argument("cidr", help="CIDR network (example: 192.168.1.0/24)")

    args = parser.parse_args()

    ports = parse_ports(args.ports)
    network = ipaddress.ip_network(args.cidr)

    print(f"\nScanning network {network}...\n")

    up_count = 0
    down_count = 0
    error_count = 0
    total_hosts = 0

    try:
        for ip in network.hosts():
            total_hosts += 1

            status, response_time = scan_host(ip)

            if status == "UP":
                up_count += 1
            elif status == "DOWN":
                down_count += 1
            else:
                error_count += 1

            print(f"{str(ip):<15} - {status} ({response_time})")

            if status == "UP":
                open_ports = []

                for port in ports:
                    if scan_port(ip, port):
                        open_ports.append(port)

                if open_ports:
                    print(f"   Open ports: {', '.join(map(str, open_ports))}")

    except KeyboardInterrupt:
        print("\n\nScan interrupted by user.")

    finally:
        print("\nScan complete!:")
        print(f"Total hosts scanned: {total_hosts}")
        print(f"Active hosts (UP): {up_count}")
        print(f"Down hosts: {down_count}")
        print(f"Errors: {error_count}")