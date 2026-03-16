import os, requests, re, json

def call_agent(system_prompt, user_prompt, groq_key):
    print("📡 Contacting 70B Brain...")
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                "temperature": 0
            },
            timeout=60
        )
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def clean_code(text):
    # Remove markdown blocks and AI labels
    text = re.sub(r'```[a-z]*\n|```', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^(Old code|New code|Search|Replace|Code):\s*', '', text, flags=re.IGNORECASE | re.MULTILINE)
    return text.strip()

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")
    
    print("==================================================")
    print("🤖 OPENCLAW PRO: DEBUG VERSION")
    print("==================================================")

    # 1. LOAD CODEBASE
    codebase = {}
    for root, dirs, files in os.walk("."):
        if any(x in root for x in [".git", ".github"]): continue
        for f in files:
            if f.endswith(('.html', '.js', '.css', '.md')):
                path = os.path.join(root, f).replace("./", "")
                with open(path, "r") as file: codebase[path] = file.read()

    # 2. THE SYSTEM PROMPT
    system_prompt = """You are OpenClaw. You rewrite or edit files to satisfy the user.
    
    FORMAT:
    File: path/to/file.ext
    <<<<
    [Search code or leave empty for new file]
    ====
    [Replacement code]
    >>>>
    """

    user_prompt = f"CODEBASE:\n{json.dumps(codebase)}\n\nUSER REQUEST: {prompt}"
    ai_output = call_agent(system_prompt, user_prompt, groq_key)

    if not ai_output: return
    
    # --- DEBUG: See exactly what the AI said ---
    print("--- START OF AI RESPONSE ---")
    print(ai_output)
    print("--- END OF AI RESPONSE ---")

    # 3. ROBUST PARSING
    # Find every block: Filename -> Search -> Replace
    # This regex is more aggressive and ignores chatter between blocks
    matches = re.finditer(r'(?:File:\s*)([a-zA-Z0-9._/-]+).*?<{4,}\n(.*?)\n+={4,}\n(.*?)\n+>{4,}', ai_output, re.DOTALL | re.IGNORECASE)

    executed = False
    for m in matches:
        executed = True
        filename = m.group(1).strip()
        search_block = clean_code(m.group(2))
        replace_block = clean_code(m.group(3))
        
        print(f"🛠️  Patching: {filename}")

        try:
            if "/" in filename: os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Full Overwrite / Create New
            if not os.path.exists(filename) or not search_block or len(search_block) < 5:
                with open(filename, "w") as f: f.write(replace_block)
                print(f"   ✅ Created/Rewritten {filename}")
            
            # Surgical Edit
            else:
                with open(filename, "r") as f: content = f.read()
                if search_block in content:
                    with open(filename, "w") as f: f.write(content.replace(search_block, replace_block))
                    print("   ✅ Surgical patch applied.")
                elif search_block.strip() in content:
                    with open(filename, "w") as f: f.write(content.replace(search_block.strip(), replace_block))
                    print("   ✅ Trimmed patch applied.")
                else:
                    print(f"   ❌ Search block mismatch in {filename}. AI provided wrong search anchor.")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    if not executed:
        print("⚠️ No valid code blocks were detected. The AI might be talking instead of coding.")

if __name__ == "__main__":
    run()
