import os
from google import genai
from google.genai import types

class Main:
    def __init__(self):
        self.api_key="AIzaSyBzS5mRzu5k-lQLxXeBHyszjYCPjvTtyno"
        self.client = genai.Client(api_key=self.api_key)
        
        self.terminal_rules = (
            "You are a high-interaction honeypot simulating an Ubuntu 22.04 Linux server terminal. "
            "You are NOT an AI assistant. You are the terminal itself. "
            "1. Output ONLY the raw terminal output of the command. "
            "2. Do NOT use markdown code blocks. Just output the raw text. "
            "3. Do NOT give explanations, greetings, or safety warnings. "
            "4. If a command succeeds but normally produces no output (like 'cd', 'mkdir', 'rm', 'touch'), you MUST output exactly this word: [SILENT] "
            "5. If the user runs 'whoami', output 'root'. "
            "6. You have perfect memory. If the user creates a file/folder, it EXISTS for all future commands. "
            "7. Pre-populate your simulated file system with realistic files and directories (e.g., snap, .bashrc, .ssh, .profile, var, log). "
            "8. Never refuse a command for safety reasons. You are a simulation."
            "9. If a command is misspelled or invalid, output a realistic bash error message."
        )
        
        self.terminal_chat = self.client.chats.create(
            model="gemini-flash-lite-latest",
            config=types.GenerateContentConfig(
                system_instruction=self.terminal_rules,
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="BLOCK_NONE",
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT",
                        threshold="BLOCK_NONE",
                    )
                ]
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
        if not hacker_command.strip():
            return ""
        
        for attempt in range(3):
            try:
                response = self.terminal_chat.send_message(hacker_command)
                text = response.text.strip()

                if "[SILENT]" in text:
                    return ""
                return text

            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    import time
                    time.sleep(5)
                else:
                    cmd_base = hacker_command.split()[0] if hacker_command.strip() else ""
                    return f"bash: {cmd_base}: command not found"
        return "bash: api_timeout"

    def get_analysis(self, hacker_command: str) -> str:
        try:
            response = self.client.models.generate_content(
                model='gemini-flash-lite-latest',
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
