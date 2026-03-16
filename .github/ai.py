import os, requests, re, json

def call_agent(system_prompt, user_prompt, groq_key):
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                "temperature": 0.1
            }
        )
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API Error: {e}")
        return None

def clean_code(text):
    """Strips markdown and AI chatter from code blocks."""
    text = re.sub(r'```[a-z]*\n|```', '', text, flags=re.IGNORECASE)
    # Remove common AI 'lazy' placeholders
    text = re.sub(r'//\s*existing code.*|/\*\s*existing code.*?\*/', '', text, flags=re.IGNORECASE)
    return text.strip()

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")
    
    print("==================================================")
    print("🤖 OPENCLAW PRO: AUTONOMOUS ENGINEER")
    print("==================================================")

    # 1. VISION: Load the codebase
    codebase = {}
    for root, dirs, files in os.walk("."):
        if any(x in root for x in [".git", ".github"]): continue
        for f in files:
            if f.endswith(('.html', '.js', '.css', '.md', '.json')):
                path = os.path.join(root, f).replace("./", "")
                with open(path, "r") as file: codebase[path] = file.read()

    # 2. THE PROMPT: Demand OpenClaw behavior
    system_prompt = """You are OpenClaw, a world-class Full-Stack Engineer.
    
    TASK: Execute the user request by modifying the codebase.
    
    PRINCIPLES:
    - MODERN UI: Use Tailwind CSS, glassmorphism, and neon aesthetics.
    - AUTONOMY: Fix broken structures automatically. Link files correctly.
    - EDITING: Use the format below for every file you touch.

    FORMAT:
    File: path/to/file.ext
    <<<<
    [Exact code to find]
    ====
    [New code to replace it with]
    >>>>
    """

    codebase_str = "\n".join([f"--- {f} ---\n{c}" for f, c in codebase.items()])
    ai_output = call_agent(system_prompt, f"CODEBASE:\n{codebase_str}\n\nREQUEST: {prompt}", groq_key)

    if not ai_output: return
    print(f"🧠 AGENT LOG:\n{ai_output[:500]}...")

    # 3. SEMANTIC PARSING: The "OpenClaw" logic
    # Split by "File:" to handle multiple files in one go
    file_sections = re.split(r'File:\s*', ai_output)[1:]

    for section in file_sections:
        try:
            filename = section.split('\n')[0].strip()
            # Find all Search/Replace blocks in this file section
            blocks = re.findall(r'<{4,}\n(.*?)\n+={4,}\n(.*?)\n+>{4,}', section, re.DOTALL)
            
            if not blocks: continue
            
            if "/" in filename: os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            for search_raw, replace_raw in blocks:
                search_text = clean_code(search_raw)
                replace_text = clean_code(replace_raw)
                
                print(f"🛠️  Patching: {filename}")

                # Create New File
                if not os.path.exists(filename) or not search_text or len(search_text) < 3:
                    with open(filename, "w") as f: f.write(replace_text)
                    print(f"   ✅ Created/Rewritten {filename}")
                
                # Surgical Patch
                else:
                    with open(filename, "r") as f: content = f.read()
                    if search_text in content:
                        with open(filename, "w") as f: f.write(content.replace(search_text, replace_text))
                        print("   ✅ Surgical patch applied.")
                    elif search_text.strip() in content:
                        with open(filename, "w") as f: f.write(content.replace(search_text.strip(), replace_text))
                        print("   ✅ Whitespace-adjusted patch applied.")
                    else:
                        print(f"   ⚠️ Search block mismatch in {filename}. Appending as fallback.")
                        with open(filename, "a") as f: f.write("\n" + replace_text)

        except Exception as e:
            print(f"   ❌ Error in section: {e}")

if __name__ == "__main__":
    run()
