import os, requests, re

def call_agent(system_prompt, user_prompt, groq_key):
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile", # 🚀 UPGRADED TO 70B GENIUS MODEL
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                "temperature": 0.1
            }
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API Error: {e}")
        return None

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")
    
    print("==================================================")
    print("🚀 OPENCLAW V3: 70B SENIOR ENGINEER ACTIVE")
    print(f"🗣️ Request: '{prompt}'")
    print("==================================================")

    # 1. READ CODEBASE
    codebase = {}
    for root, dirs, files in os.walk("."):
        if any(x in root for x in [".git", ".github", "__pycache__"]): continue
        for f in files:
            if f.endswith(('.html', '.js', '.css', '.md', '.json', '.txt')):
                filepath = os.path.join(root, f).replace("./", "")
                try:
                    with open(filepath, "r") as file:
                        content = file.read()
                        if len(content) < 15000: codebase[filepath] = content
                except: pass

    # 2. THE AIDER-STYLE SYSTEM PROMPT
    system_prompt = """You are an Elite Frontend Engineer.
    1. UI RULES: Use Tailwind CSS extensively. Create modern, glassmorphism, dark-themed UIs. Make it look like a high-end AI startup.
    2. HTML RULES: Do not put raw HTML outside of <body>.
    
    You edit files by outputting SEARCH/REPLACE blocks.
    
    FORMAT RULES:
    File: path/to/file.ext
    <<<<
    Exact lines of original code to replace
    ====
    New lines of code to insert
    >>>>
    
    - To create a new file, leave the <<<< section empty.
    - You can use multiple blocks.
    - Explain your design thoughts first, then output the blocks."""

    codebase_str = ""
    for file, code in codebase.items():
        codebase_str += f"\n--- FILE: {file} ---\n{code}\n"

    user_prompt = f"CODEBASE:\n{codebase_str}\n\nUSER REQUEST: {prompt}"

    print("🧠 Analyzing architecture with 70B Model...")
    plan_text = call_agent(system_prompt, user_prompt, groq_key)

    if not plan_text:
        print("❌ Agent failed to respond.")
        return

    # 3. PARSE AND EXECUTE BLOCKS
    # Regex to find: File: filename \n <<<< \n search \n ==== \n replace \n >>>>
    blocks = re.finditer(r'File:\s*([^\n]+)\n+<<<<\n(.*?)\n+====\n(.*?)\n+>>>>', plan_text, re.DOTALL)
    
    executed = False
    for match in blocks:
        executed = True
        target_file = match.group(1).strip()
        search_text = match.group(2).strip('\n')
        replace_text = match.group(3).strip('\n')
        
        print(f"✂️  Targeting: {target_file}")
        
        try:
            if "/" in target_file: os.makedirs(os.path.dirname(target_file), exist_ok=True)
            
            # Create new file
            if not os.path.exists(target_file) or search_text == "":
                with open(target_file, "w") as f: f.write(replace_text)
                print("   ✅ Created/Overwritten successfully.")
                continue
                
            # Edit existing file
            with open(target_file, "r") as f: current_code = f.read()
            
            if search_text in current_code:
                new_code = current_code.replace(search_text, replace_text)
                with open(target_file, "w") as f: f.write(new_code)
                print("   ✅ Surgical replace successful.")
            elif search_text.strip() in current_code:
                new_code = current_code.replace(search_text.strip(), replace_text)
                with open(target_file, "w") as f: f.write(new_code)
                print("   ✅ Fallback replace successful (ignored whitespace).")
            else:
                print("   ❌ ABORTED: Could not find exact search text in file to replace. Code safe.")
                
        except Exception as e:
            print(f"   ❌ Error applying block: {e}")

    if not executed:
        print("⚠️ No valid edit blocks found in AI response.")
        print(f"RAW OUTPUT:\n{plan_text}")

if __name__ == "__main__":
    run()
