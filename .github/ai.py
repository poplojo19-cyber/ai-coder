import os, requests, re, json

def call_agent(system_prompt, user_prompt, groq_key):
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
        print(f"❌ API Error: {e}")
        return None

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")
    
    print("==================================================")
    print("🤖 OPENCLAW: SIMPLE GITHUB EDITOR ACTIVE")
    print("==================================================")

    # 1. LOAD CODEBASE
    codebase = {}
    for root, dirs, files in os.walk("."):
        if any(x in root for x in [".git", ".github"]): continue
        for f in files:
            if f.endswith(('.html', '.js', '.css', '.md')):
                path = os.path.join(root, f).replace("./", "")
                with open(path, "r") as file: codebase[path] = file.read()

    # 2. THE SYSTEM PROMPT (Ultra-Simplified)
    system_prompt = """You are a GitHub File Editor.
    Your only job is to edit files using this exact format:

    File: [filename]
    <<<<
    [One or two unique lines to find]
    ====
    [The new code to replace those lines with]
    >>>>
    
    If creating a new file, leave the area between <<<< and ==== empty.
    """

    user_prompt = f"FILES:\n{json.dumps(codebase)}\n\nTASK: {prompt}"
    ai_output = call_agent(system_prompt, user_prompt, groq_key)

    if not ai_output: return
    
    print("--- AI RESPONSE ---")
    print(ai_output)
    print("-------------------")

    # 3. ROBUST PARSING
    # Find the filename even if "File:" is missing (it will look for common extensions)
    # or it will grab it from the prompt context.
    
    # We split by filename or block markers
    blocks = re.findall(r'(?:File:\s*)?([a-zA-Z0-9._/-]+\.[a-z]+)?\s*\n?<{4,}\n(.*?)\n+={4,}\n(.*?)\n+>{4,}', ai_output, re.DOTALL)

    if not blocks:
        # Fallback: If no filename was found in the markers, try to find it in the text
        print("⚠️ No filename in markers. Checking text...")
        potential_file = re.search(r'([a-zA-Z0-9._/-]+\.[a-z]+)', ai_output)
        filename_fallback = potential_file.group(1) if potential_file else "index.html"
        blocks = re.findall(r'<{4,}\n(.*?)\n+={4,}\n(.*?)\n+>{4,}', ai_output, re.DOTALL)
        blocks = [(filename_fallback, b[0], b[1]) for b in blocks]

    for filename, search_raw, replace_raw in blocks:
        filename = filename.strip()
        search_text = search_raw.strip('\r\n')
        replace_text = replace_raw.strip('\r\n')
        
        print(f"🛠️  Patching: {filename}")

        if not os.path.exists(filename):
            with open(filename, "w") as f: f.write(replace_text)
            print(f"   ✅ Created {filename}")
            continue

        with open(filename, "r") as f: content = f.read()

        # SURGICAL STRIP MATCH
        # We strip spaces from every line to make it impossible to miss
        search_lines = [l.strip() for l in search_text.split('\n') if l.strip()]
        content_lines = content.split('\n')
        
        found = False
        for i in range(len(content_lines) - len(search_lines) + 1):
            if all(content_lines[i+j].strip() == search_lines[j] for j in range(len(search_lines))):
                # We found the spot!
                # Keep the indentation of the original first line
                indent = content_lines[i][:content_lines[i].find(content_lines[i].strip())]
                new_lines = [indent + l if l.strip() else l for l in replace_text.split('\n')]
                
                content_lines[i:i+len(search_lines)] = new_lines
                content = '\n'.join(content_lines)
                found = True
                break
        
        if found:
            with open(filename, "w") as f: f.write(content)
            print("   ✅ Edit successful.")
        else:
            print(f"   ❌ ERROR: Could not find the code to edit in {filename}.")

    print("==================================================")
    print("🎉 DONE")
