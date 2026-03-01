import socket 
import threading
import csv
from datetime import datetime
from chameleon import Main
import re 

PORT = 5050
SERVER = "0.0.0.0"  
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

def clean_terminal_input(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    
    result = []
    for char in text:
        if char in ('\x08', '\x7f'):  # If it's a Backspace or Delete
            if result:
                result.pop() # Actually delete the previous character
        else:
            result.append(char)
    return "".join(result)

def log_attack(ip, command, response_type): 
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("attacks.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, ip, command, response_type])

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR) 

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    ai_engine = Main()

    # 1. Send a Fake Welcome Message (looks like Linux)
    welcome_msg = "Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-91-generic x86_64)\r\nadmin@server:~$ "
    conn.send(welcome_msg.encode(FORMAT))

    buffer = "" #adding this to resolve issue of getting response of every letter without hitting enter

    connected = True

    while connected: 
        try: 
            # 2. Receive Raw Data (No Headers!)
            # We read 1024 bytes at a time
            msg = conn.recv(1024)
            if not msg:
                break
            
            text = msg.decode(FORMAT)
            buffer += text

            if "\n" in buffer or "\r" in buffer: 
                if "\r\n" in buffer:
                    cmd, rest = buffer.split("\r\n", 1)
                elif "\n" in buffer:
                    cmd, rest = buffer.split("\n", 1)
                else:
                    cmd, rest = buffer.split("\r", 1)

                buffer = rest
                cmd = clean_terminal_input(cmd).strip()
                print(f"[{addr}] COMMAND: {cmd}")

                #Ask ai for output
                if cmd:
                    fake_output = ai_engine.get_terminal_response(cmd)
                    explaination = ai_engine.get_analysis(cmd)

                    log_attack(addr[0], cmd, explaination)
                    print(f"   -> Analyst: {explaination}")

                    if fake_output:
                        fake_output = fake_output.replace('\n', '\r\n')
                        response = f"\r\n{fake_output}\r\nroot@ubuntu:~# "

                    else:
                        response = f"\r\nroot@ubuntu:~# "
                    conn.send(response.encode(FORMAT))
                else:
                    conn.send("\r\nadmin@server:~$ ".encode(FORMAT))
        except ConnectionResetError: 
            break

    print(f"[DISCONNECT] {addr} disconnected.")
    conn.close()


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}:{PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting...")
start()

