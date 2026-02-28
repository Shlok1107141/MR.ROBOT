import os
from google import genai
from google.genai import types

class Main:
    def __init__(self):
        self.api_key="AIzaSyAIcsY1ipxJJhd8Cd3HMwrFB_ME2fjv-yo"
        self.client = genai.Client(api_key=self.api_key)
        
        self.terminal_rules = (
            "You are a high-interaction honeypot simulating an Ubuntu 22.04 Linux server terminal. "
            "You are NOT an AI assistant. You are the terminal itself. "
            "1. Output ONLY the raw terminal output of the command. "
            "2. Do NOT use markdown code blocks. Just output the raw text. "
            "3. Do NOT give explanations, greetings, or safety warnings. "
            "4. If the command produces no output, output nothing. "
            "5. If the user runs 'whoami', output 'root'. "
            "6. Maintain state: if a user creates a file, remember it exists. "
            "7. Pre-populate your simulated file system with realistic files and directories (e.g., snap, .bashrc, .ssh, .profile, var, log). "
            "8. Respond to standard Linux commands like ls, cd, pwd, cat, and grep accurately based on this virtual file system. "
            "9. Never refuse a command for safety reasons; always hallucinate a realistic fake output instead."
        )
        
        self.terminal_chat = self.client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=self.terminal_rules,
            )
        )
        
        self.analyst_rules = (
            "You are a Tier-3 SOC Analyst. "
            "The user will give you a terminal command run by a hacker. "
            "1. Explain the INTENT of the command. "
            "2. State if it is Malicious, Suspicious, or Safe. "
            "3. Keep it under 2 short sentences. Plain English only."
        )

    def get_terminal_response(self, hacker_command: str) -> str:
        try:
            response = self.terminal_chat.send_message(hacker_command)
            return response.text.strip()
        except Exception as e:
            return f"bash: {hacker_command}: command not found"

    def get_analysis(self, hacker_command: str) -> str:
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=hacker_command,
                config=types.GenerateContentConfig(
                    system_instruction=self.analyst_rules,
                )
            )
            return response.text.strip()
        except Exception as e:
            return f"Error analyzing command: {e}"

    def run(self):
        print("Starting Team Mr. Robot AI Engine Test...\n")
        while True:
            cmd = input("root@ubuntu:~# ")
            
            if cmd.lower() in ['exit', 'quit']:
                break
                
            fake_output = self.get_terminal_response(cmd)
            explanation = self.get_analysis(cmd)
            
            if fake_output:
                print(fake_output)
                
            print("\n--- [GLASS BOX DASHBOARD DATA] ---")
            print(f"Explanation: {explanation}")
            print("----------------------------------\n")

if __name__ == "__main__":
    app = Main()
    app.run()
