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

def find_and_replace(content, search_block, replace_block):
    """Finds a block in the content ignoring leading/trailing whitespace on each line."""
    search_lines = [line.strip() for line in search_block.strip().split('\n') if line.strip()]
    content_lines = content.split('\n')
    
    if not search_lines:
        return content + "\n" + replace_block

    # Look for a sequence of lines in content that match search_lines when stripped
    for i in range(len(content_lines) - len(search_lines) + 1):
        match = True
        for j in range(len(search_lines)):
            if content_lines[i + j].strip() != search_lines[j]:
                match = False
                break
        
        if match:
            # We found it! Identify the original indentation of the first line
            indent = content_lines[i][:content_lines[i].find(content_lines[i].strip())]
            # Apply that indentation to all new lines
            indented_replace = '\n'.join([indent + line if line.strip() else line for line in replace_block.strip('\n').split('\n')])
            
            new_content_lines = content_lines[:i] + [indented_replace] + content_lines[i + len(search_lines):]
            return '\n'.join(new_content_lines)
            
    return None

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")
    
    print("==================================================")
    print("🤖 OPENCLAW: GIT-PATCH ENGINE ACTIVE")
    print("==================================================")

    # 1. LOAD CODEBASE
    codebase = {}
    for root, dirs, files in os.walk("."):
        if any(x in root for x in [".git", ".github"]): continue
        for f in files:
            if f.endswith(('.html', '.js', '.css', '.md')):
                path = os.path.join(root, f).replace("./", "")
                with open(path, "r") as file: codebase[path] = file.read()

    # 2. THE SYSTEM PROMPT (Strict & Professional)
    system_prompt = """You are a Senior GitHub Git-Patch Expert. 
    Your ONLY job is to provide SEARCH/REPLACE blocks for file edits.
    
    RULES:
    1. Your SEARCH block must contain enough unique lines to identify the location.
    2. Do not worry about indentation; the system handles it.
    3. Use the exact markers: <<<<, ====, >>>>.
    """

    user_prompt = f"CODEBASE:\n{json.dumps(codebase)}\n\nUSER REQUEST: {prompt}"
    ai_output = call_agent(system_prompt, user_prompt, groq_key)

    if not ai_output: return
    
    print("--- RAW AI BRAIN OUTPUT ---")
    print(ai_output)
    print("---------------------------")

    # 3. PARSING
    # Normalize markers
    processed = re.sub(r'<+\s*<+', '<<<<', ai_output)
    processed = re.sub(r'=+\s*=+', '====', processed)
    processed = re.sub(r'>+\s*>+', '>>>>', processed)

    file_sections = re.split(r'File:\s*', processed)[1:]

    for section in file_sections:
        filename = section.split('\n')[0].strip()
        blocks = re.findall(r'<{4,}\n(.*?)\n+={4,}\n(.*?)\n+>{4,}', section, re.DOTALL)
        
        if not blocks: continue
        
        print(f"🛠️  Patching: {filename}")
        if "/" in filename: os.makedirs(os.path.dirname(filename), exist_ok=True)

        if not os.path.exists(filename):
            with open(filename, "w") as f: f.write(blocks[0][1].strip())
            print(f"   ✅ Created new file.")
            continue

        with open(filename, "r") as f: content = f.read()

        for search_raw, replace_raw in blocks:
            result = find_and_replace(content, search_raw, replace_raw)
            if result:
                content = result
                print("   ✅ Surgical patch applied successfully.")
            else:
                print(f"   ❌ ERROR: Could not find code block in {filename}.")
        
        with open(filename, "w") as f: f.write(content)

    print("==================================================")
    print("🎉 ALL TASKS COMPLETED")

if __name__ == "__main__":
    run()
