import os, json, requests, re

def call_ai(system_prompt, user_prompt, groq_key):
    """Sends a request to Groq and returns the text response."""
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1
            }
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq API Error: {e}")
        if 'resp' in locals(): print(f"Response: {resp.text}")
        return None

def extract_json(text):
    """Safely extracts the first JSON object from a string."""
    try:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
        return None
    except:
        return None

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")

    print("========================================")
    print(f"🚀 INITIALIZING OPENCLAW AGENT")
    print(f"Task: {prompt}")
    print("========================================")

    # ---------------------------------------------------------
    # PHASE 1: DISCOVERY & MEMORY (The Eyes and Brain)
    # ---------------------------------------------------------
    all_files = []
    for root, dirs, files in os.walk("."):
        if any(x in root for x in [".git", ".github", "__pycache__"]): continue
        for f in files:
            all_files.append(os.path.join(root, f).replace("./", ""))
    
    print(f"📂 Discovered files: {all_files}")

    history = []
    if os.path.exists("memory.json"):
        try:
            with open("memory.json", "r") as f: history = json.load(f)
        except:
            history = []

    # ---------------------------------------------------------
    # PHASE 2: PLANNING (The Decision)
    # ---------------------------------------------------------
    print("🧠 Thinking about the architecture...")
    plan_system = """You are a Senior Software Architect. 
    Review the requested task, the existing files, and the history.
    Decide WHICH file needs to be modified or created.
    Respond ONLY with a valid JSON object in this format:
    {"file": "filename.ext", "reasoning": "Why this file"}"""
    
    plan_user = f"Files: {all_files}\nHistory: {history}\nTask: {prompt}"
    
    plan_response = call_ai(plan_system, plan_user, groq_key)
    plan = extract_json(plan_response)
    
    if not plan:
        print(f"❌ Planning Failed. Raw output: {plan_response}")
        return

    target_file = plan["file"]
    print(f"🎯 Target Acquired: {target_file}")
    print(f"💡 Reasoning: {plan.get('reasoning', 'No reasoning provided')}")

    # ---------------------------------------------------------
    # PHASE 3: PREPARATION (Reading the target)
    # ---------------------------------------------------------
    original_lines = []
    if os.path.exists(target_file):
        with open(target_file, "r") as f: 
            original_lines = f.read().split('\n')
    else:
        print(f"✨ File '{target_file}' does not exist. It will be created.")
        original_lines = [""]

    # Number the lines so the AI knows exactly where to edit
    numbered_code = '\n'.join([f"{i+1}: {line}" for i, line in enumerate(original_lines)])

    # ---------------------------------------------------------
    # PHASE 4: EXECUTION (Surgical Editing)
    # ---------------------------------------------------------
    print(f"✍️  Calculating line modifications for {target_file}...")
    edit_system = f"""You are an elite coding agent. You are editing '{target_file}'.
    CRITICAL RULES:
    1. DO NOT rewrite the whole file unless asked. Only replace the specific lines that need changing.
    2. If adding new code to the end of the file, use the last line number.
    3. If creating a new file, use START_LINE: 1 and END_LINE: 1.
    4. You MUST format your response EXACTLY like this:
    
    START_LINE: <number>
    END_LINE: <number>
    [CODE_START]
    <the exact code to insert>
    [CODE_END]"""

    edit_user = f"Current Content of {target_file}:\n{numbered_code}\n\nTask: {prompt}"
    
    edit_response = call_ai(edit_system, edit_user, groq_key)
    if not edit_response:
        print("❌ Execution Failed: No response from Groq.")
        return

    # ---------------------------------------------------------
    # PHASE 5: PARSING & APPLYING (The Hands)
    # ---------------------------------------------------------
    try:
        s_line = int(re.search(r'START_LINE:\s*(\d+)', edit_response).group(1))
        e_line = int(re.search(r'END_LINE:\s*(\d+)', edit_response).group(1))
        
        # Extract the code and strip accidental markdown blocks (```html ... ```)
        raw_code = re.search(r'\[CODE_START\](.*?)\[CODE_END\]', edit_response, re.DOTALL).group(1).strip('\n')
        clean_code = re.sub(r'^```[a-z]*\n|```$', '', raw_code, flags=re.MULTILINE).strip('\n')
        
        new_code_lines = clean_code.split('\n')

        # Safety padding if AI tries to write past the end of the file
        while len(original_lines) < e_line:
            original_lines.append("")

        # SURGICAL SPLICE: Replace only the targeted lines
        original_lines[max(0, s_line-1) : e_line] = new_code_lines
        
        with open(target_file, "w") as f: 
            f.write('\n'.join(original_lines))
            
        print(f"✅ Successfully modified lines {s_line} to {e_line} in {target_file}")
        
        # Save to memory (Keep last 10 tasks)
        history.append({"task": prompt, "file": target_file})
        with open("memory.json", "w") as f: 
            json.dump(history[-10:], f, indent=2)

    except Exception as e:
        print(f"❌ Failed to parse or apply edit.")
        print(f"Error: {e}")
        print(f"Raw AI Output:\n{edit_response}")

if __name__ == "__main__":
    run()
