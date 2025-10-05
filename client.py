import socket
import pickle
import struct
import cv2
import sys
import os
import time
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
    print(f"{Colors.CYAN}                    [CLIENT MODULE]{Colors.RESET}")
    print(f"{Colors.WHITE}{'─' * 70}{Colors.RESET}\n")
def install_dependencies():
    required = {
        'opencv-python': 'cv2',
        'colorama': 'colorama'
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
def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unable to detect"
def start_client():
    print_banner()
    local_ip = get_local_ip()
    print(f"{Colors.PURPLE}[•] Your local IP address: {Colors.WHITE}{local_ip}{Colors.RESET}")
    print(f"{Colors.YELLOW}[!] Share this IP with the server operator{Colors.RESET}\n")
    server_ip = input(f"{Colors.GREEN}[→] Enter the server's IP to connect: {Colors.RESET}").strip()
    if not server_ip:
        print(f"{Colors.RED}[✗] Error: IP address cannot be empty!{Colors.RESET}")
        return
    PORT = 9999
    print(f"\n{Colors.CYAN}[*] Initializing RoftCam Client...{Colors.RESET}")
    print(f"{Colors.WHITE}{'─' * 70}{Colors.RESET}")
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"{Colors.PURPLE}[•] Attempting to connect to: {Colors.WHITE}{server_ip}:{PORT}{Colors.RESET}")
        client_socket.connect((server_ip, PORT))
        print(f"{Colors.GREEN}[✓] Connected to server successfully!{Colors.RESET}")
        print(f"{Colors.CYAN}[*] Initializing camera...{Colors.RESET}")
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        camera.set(cv2.CAP_PROP_FPS, 30)
        if not camera.isOpened():
            print(f"{Colors.RED}[✗] Error: Could not access camera!{Colors.RESET}")
            return
        print(f"{Colors.GREEN}[✓] Camera initialized successfully!{Colors.RESET}")
        print(f"{Colors.CYAN}[*] Starting video transmission...{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] Press Ctrl+C to stop transmission{Colors.RESET}")
        print(f"{Colors.WHITE}{'─' * 70}{Colors.RESET}\n")
        frame_count = 0
        start_time = time.time()
        while True:
            ret, frame = camera.read()
            if not ret:
                print(f"{Colors.RED}[✗] Failed to capture frame{Colors.RESET}")
                break
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            result, encoded_frame = cv2.imencode('.jpg', frame, encode_param)
            if not result:
                continue
            data = pickle.dumps(encoded_frame)
            message = struct.pack("Q", len(data)) + data
            try:
                client_socket.sendall(message)
                frame_count += 1
                if frame_count % 100 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"{Colors.GREEN}[✓] Frames sent: {Colors.WHITE}{frame_count} {Colors.PURPLE}| "
                          f"{Colors.CYAN}FPS: {Colors.WHITE}{fps:.2f}{Colors.RESET}")
            except socket.error as e:
                print(f"\n{Colors.RED}[✗] Connection lost: {str(e)}{Colors.RESET}")
                break
        camera.release()
        client_socket.close()
        print(f"\n{Colors.YELLOW}[!] Transmission stopped{Colors.RESET}")
        print(f"{Colors.PURPLE}[•] Total frames sent: {Colors.WHITE}{frame_count}{Colors.RESET}")
    except socket.error as e:
        print(f"{Colors.RED}[✗] Connection error: {str(e)}{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] Make sure the server is running and the IP is correct{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[✗] Error: {str(e)}{Colors.RESET}")
    finally:
        try:
            camera.release()
        except:
            pass

if __name__ == "__main__":
    try:
        install_dependencies()
        start_client()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Client interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[✗] Fatal error: {str(e)}{Colors.RESET}")
