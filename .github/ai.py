import os, requests, re

def call_agent(system_prompt, user_prompt, groq_key):
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
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
    print("🤖 OPENCLAW UNBREAKABLE AUTONOMOUS ENGINEER")
    print(f"🗣️ User Request: '{prompt}'")
    print("==================================================")

    # 1. READ ENTIRE CODEBASE
    codebase = {}
    for root, dirs, files in os.walk("."):
        if any(x in root for x in [".git", ".github", "__pycache__"]): continue
        for f in files:
            if f.endswith(('.html', '.js', '.css', '.md', '.json', '.txt')):
                filepath = os.path.join(root, f).replace("./", "")
                try:
                    with open(filepath, "r") as file:
                        content = file.read()
                        if len(content) < 15000: # Protect against massive files
                            codebase[filepath] = content
                except: pass

    # 2. THE UNBREAKABLE SYSTEM PROMPT
    # We use tags like <edit> instead of JSON so it never crashes.
    system_prompt = """You are an Elite Autonomous Frontend Engineer.
    You receive the current codebase and a user request.
    
    YOUR RULES:
    1. AESTHETICS: Use Tailwind CSS, glassmorphism, flexbox/grid, and professional colors. Make it look like a modern AI startup.
    2. ARCHITECTURE: HTML inside <body>. CSS in <head>. Scripts at bottom of <body>. Fix broken structures.
    
    RESPOND EXACTLY IN THIS TEXT FORMAT (DO NOT USE JSON):
    
    THOUGHTS:
    Explain your architectural decisions here.

    <create file="path/to/new.ext">
    [code for the new file here]
    </create>

    <edit file="path/to/existing.ext">
    <search>
    [Exact old code block to replace]
    </search>
    <replace>
    [The new code that replaces the old code]
    </replace>
    </edit>
    
    You can use multiple <create> or <edit> blocks. Ensure <search> blocks EXACTLY match the existing code."""

    # We format the codebase into a clean string
    codebase_str = ""
    for file, code in codebase.items():
        codebase_str += f"\n--- FILE: {file} ---\n{code}\n"

    user_prompt = f"CODEBASE STATE:\n{codebase_str}\n\nUSER REQUEST: {prompt}\n\nExecute the plan."

    print("🧠 Analyzing codebase and formulating architecture...")
    plan_text = call_agent(system_prompt, user_prompt, groq_key)

    if not plan_text:
        print("❌ Agent failed to generate a plan.")
        return

    # Extract thoughts
    thoughts_match = re.search(r'THOUGHTS:\s*(.*?)(?=<create|<edit|$)', plan_text, re.DOTALL)
    print(f"💡 AGENT THOUGHTS: {thoughts_match.group(1).strip() if thoughts_match else 'Executing...'}")
    print("--------------------------------------------------")

    # 3. EXECUTE <create> BLOCKS
    creates = re.finditer(r'<create file="(.*?)">(.*?)</create>', plan_text, re.DOTALL)
    for match in creates:
        target_file = match.group(1)
        code = match.group(2).strip('\n')
        
        print(f"📁 Action: CREATE -> {target_file}")
        try:
            if "/" in target_file: os.makedirs(os.path.dirname(target_file), exist_ok=True)
            with open(target_file, "w") as f: f.write(code)
            print("   ✅ File created successfully.")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

    # 4. EXECUTE <edit> BLOCKS
    edits = re.finditer(r'<edit file="(.*?)">\s*<search>(.*?)</search>\s*<replace>(.*?)</replace>\s*</edit>', plan_text, re.DOTALL)
    for match in edits:
        target_file = match.group(1)
        search_text = match.group(2).strip('\n')
        replace_text = match.group(3).strip('\n')
        
        print(f"✂️  Action: EDIT -> {target_file}")
        try:
            if os.path.exists(target_file):
                with open(target_file, "r") as f: current_code = f.read()
                
                # Strict Search
                if search_text in current_code:
                    with open(target_file, "w") as f: f.write(current_code.replace(search_text, replace_text))
                    print("   ✅ Surgical block replacement successful.")
                # Fallback: Ignore leading/trailing whitespace
                elif search_text.strip() in current_code:
                    with open(target_file, "w") as f: f.write(current_code.replace(search_text.strip(), replace_text))
                    print("   ✅ Fallback replacement successful (ignored whitespace).")
                else:
                    print("   ⚠️ Search block not found. Appending to end of file as failsafe.")
                    with open(target_file, "a") as f: f.write("\n" + replace_text)
            else:
                print("   ❌ Target file does not exist.")
        except Exception as e:
            print(f"   ❌ Execution error: {e}")

    print("==================================================")
    print("🎉 ALL TASKS COMPLETED")

if __name__ == "__main__":
    run()
