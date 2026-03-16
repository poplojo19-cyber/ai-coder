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
    """Strips markdown and AI chatter."""
    text = re.sub(r'```[a-z]*\n|```', '', text, flags=re.IGNORECASE)
    return text.strip()

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")
    
    print("==================================================")
    print("🤖 OPENCLAW PRO: ADAPTIVE PARSER ACTIVE")
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
    system_prompt = """You are OpenClaw, a Senior Engineer.
    Modify the files by using SEARCH/REPLACE blocks.
    
    FORMAT:
    File: filename
    <<<<
    [Old code]
    ====
    [New code]
    >>>>
    """

    user_prompt = f"CODEBASE:\n{json.dumps(codebase)}\n\nREQUEST: {prompt}"
    ai_output = call_agent(system_prompt, user_prompt, groq_key)

    if not ai_output: return
    
    # --- NORMALIZATION (The Fix) ---
    # This turns "<< <<", "<<<<<", or "<<<" into a standard "[[SEARCH]]" token
    # This turns "== =", "====", or "===" into a standard "[[DIVIDER]]" token
    # This turns ">> >>", ">>>>>", or ">>>" into a standard "[[END]]" token
    processed = re.sub(r'<+\s*<+', '[[SEARCH]]', ai_output)
    processed = re.sub(r'=+\s*=+', '[[DIVIDER]]', processed)
    processed = re.sub(r'>+\s*>+', '[[END]]', processed)

    print("--- RAW AI BRAIN OUTPUT ---")
    print(ai_output)
    print("---------------------------")

    # 3. ADAPTIVE PARSING
    # Find: File: (name) ... [[SEARCH]] (content) [[DIVIDER]] (content) [[END]]
    file_sections = re.split(r'File:\s*', processed)[1:]

    if not file_sections:
        print("⚠️ No file targets detected.")

    for section in file_sections:
        try:
            filename = section.split('\n')[0].strip()
            blocks = re.findall(r'\[\[SEARCH\]\](.*?)\n?\[\[DIVIDER\]\](.*?)\n?\[\[END\]\]', section, re.DOTALL)
            
            if not blocks: continue
            
            print(f"🛠️  Patching: {filename}")
            if "/" in filename: os.makedirs(os.path.dirname(filename), exist_ok=True)

            if not os.path.exists(filename):
                # Create new file
                with open(filename, "w") as f: f.write(clean_code(blocks[0][1]))
                print(f"   ✅ Created {filename}")
                continue

            with open(filename, "r") as f: content = f.read()

            for search_raw, replace_raw in blocks:
                search_text = clean_code(search_raw)
                replace_text = clean_code(replace_raw)

                if not search_text or len(search_text) < 3:
                    # If search is empty, AI wants to overwrite/append
                    with open(filename, "a") as f: f.write("\n" + replace_text)
                    print(f"   ✅ Appended to {filename}")
                elif search_text in content:
                    content = content.replace(search_text, replace_text)
                    print(f"   ✅ Surgical patch applied.")
                elif search_text.strip() in content:
                    content = content.replace(search_text.strip(), replace_text)
                    print(f"   ✅ Whitespace-adjusted patch applied.")
                else:
                    print(f"   ❌ Search block mismatch in {filename}.")
            
            with open(filename, "w") as f: f.write(content)

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("==================================================")
    print("🎉 ALL TASKS COMPLETED")

if __name__ == "__main__":
    run()
