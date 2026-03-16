import os, requests, re, json

def call_agent(system_prompt, user_prompt, groq_key):
    print("📡 Contacting 70B Brain (this can take 20-40 seconds)...")
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
        if resp.status_code != 200:
            print(f"❌ API Error {resp.status_code}: {resp.text}")
            return None
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

def clean_code(text):
    text = re.sub(r'```[a-z]*\n|```', '', text, flags=re.IGNORECASE)
    return text.strip()

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")
    
    print("==================================================")
    print("🤖 OPENCLAW PRO: SEMANTIC PATCHER v2")
    print("==================================================")

    # 1. LOAD CODEBASE (Ignoring internal AI files to save space)
    codebase = {}
    ignore_list = [".git", ".github", "package-lock.json", "node_modules"]
    for root, dirs, files in os.walk("."):
        if any(x in root for x in ignore_list): continue
        for f in files:
            if f.endswith(('.html', '.js', '.css', '.md', '.json')):
                path = os.path.join(root, f).replace("./", "")
                with open(path, "r") as file: codebase[path] = file.read()

    print(f"👁️ Scanned {len(codebase)} files. Analyzing architecture...")

    # 2. THE SYSTEM PROMPT
    system_prompt = """You are OpenClaw, a Senior Software Engineer. 
    You perform SURGICAL edits on code.
    
    FORMAT FOR EDITS:
    File: path/to/file.ext
    <<<<
    [EXACT code block to find]
    ====
    [New code to replace it with]
    >>>>
    """

    user_prompt = f"CODEBASE:\n{json.dumps(codebase)}\n\nREQUEST: {prompt}"
    ai_output = call_agent(system_prompt, user_prompt, groq_key)

    if not ai_output:
        print("❌ System Failure: No response from the brain.")
        return
    
    # 3. PARSING
    print("🧠 AI Response received. Processing patches...")
    sections = re.split(r'File:\s*', ai_output)[1:]

    if not sections:
        print(f"⚠️ No instructions found. AI said:\n{ai_output}")
        return

    for section in sections:
        try:
            filename = section.split('\n')[0].strip()
            blocks = re.findall(r'<{4,}\n(.*?)\n+={4,}\n(.*?)\n+>{4,}', section, re.DOTALL)
            
            if not blocks: continue
            
            # Create Folder if needed
            if "/" in filename: os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # If creating new file
            if not os.path.exists(filename):
                with open(filename, "w") as f: f.write(clean_code(blocks[0][1]))
                print(f"✅ Created: {filename}")
                continue

            with open(filename, "r") as f: content = f.read()
            
            for search_raw, replace_raw in blocks:
                search_text = clean_code(search_raw)
                replace_text = clean_code(replace_raw)
                
                if not search_text or search_text in ["", " "]:
                    # If AI forgot search text, treat as append
                    with open(filename, "a") as f: f.write("\n" + replace_text)
                    print(f"✅ Appended to {filename}")
                elif search_text in content:
                    content = content.replace(search_text, replace_text)
                    print(f"✅ Surgical patch applied to {filename}")
                elif search_text.strip() in content:
                    content = content.replace(search_text.strip(), replace_text)
                    print(f"✅ Whitespace-adjusted patch applied to {filename}")
                else:
                    print(f"❌ Mismatch in {filename}. AI provided wrong search anchor.")

            with open(filename, "w") as f: f.write(content)

        except Exception as e:
            print(f"❌ Error patching {filename}: {e}")

    print("==================================================")
    print("🎉 ALL TASKS COMPLETED")

if __name__ == "__main__":
    run()
