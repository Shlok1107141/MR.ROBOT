import socket 
import threading
import google.generativeai as genai
import csv
from datetime import datetime

PORT = 5050
SERVER = "0.0.0.0"  #get ip address
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

#Ai setup
GOOGLE_API_KEY = "AIzaSyCust4_MkB6Bvk2v5HmFxI2_4HqjBjDGvo"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# The personality of your server
SYSTEM_PROMPT = """
You are a fake Ubuntu Linux server.
The user is a hacker. You must output EXACTLY what the terminal would output.

CRITICAL RULES:
1. Do NOT use Markdown formatting. NO backticks (`). NO code blocks.
2. Do NOT add headers or explanations.
3. If a command (like 'cd' or 'mkdir') succeeds, output NOTHING (empty string).
4. If a command fails, output a standard Linux error message.
5. Maintain a realistic file system.
"""

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR) 

def get_ai_response(command):
    try:
        response = model.generate_content(f"{SYSTEM_PROMPT}\n The hacker typed: {command}")
        return response.text
    except Exception as e:
        return f"\nError generating response: {e}\n"

def log_attack(ip, command, response_type): 
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("attacks.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, ip, command, response_type])


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

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
                cmd = cmd.strip()
                print(f"[{addr}] COMMAND: {cmd}")
                log_attack(addr[0], cmd, "AI_Generated")

                #Ask ai for output
                if cmd:
                    output = get_ai_response(cmd)
                    response = f"\r\n{output}\r\nadmin@server:~$ "
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

