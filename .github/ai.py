import os, requests, re, json
from difflib import SequenceMatcher

def call_agent(system_prompt, user_prompt, groq_key):
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                "temperature": 0
            }
        )
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API Error: {e}")
        return None

def fuzzy_find(needle, haystack):
    """Finds the best match for a block of code even if indentation is slightly off."""
    needle = needle.strip()
    if not needle: return None
    
    # Try exact match first
    if needle in haystack:
        return needle

    # Try whitespace-insensitive match
    n_needle = re.sub(r'\s+', '', needle)
    n_haystack = re.sub(r'\s+', '', haystack)
    
    if n_needle in n_haystack:
        # If it exists, find the start and end in the original text
        # This is a bit complex, so we'll use a simpler 'sliding window' or just return the closest block
        lines_h = haystack.splitlines()
        lines_n = needle.splitlines()
        
        for i in range(len(lines_h) - len(lines_n) + 1):
            window = "\n".join(lines_h[i : i + len(lines_n)])
            if re.sub(r'\s+', '', window) == n_needle:
                return window
    return None

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")
    
    print("==================================================")
    print("🤖 OPENCLAW PRO: SEMANTIC PATCHER ACTIVE")
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
    system_prompt = """You are OpenClaw, a Senior Full-Stack Engineer.
    Modify the codebase to satisfy the user request.
    
    RULES:
    1. SURGICAL EDITS ONLY: Provide a unique SEARCH block from the file and a REPLACE block.
    2. NO PLACEHOLDERS: Do not use 'existing code'. Copy the actual code you are replacing.
    3. DESIGN: Use Tailwind CSS. Modern, dark, glowing UI.

    FORMAT:
    File: path/to/file.ext
    SEARCH
    <<<<
    [Exact code to find]
    ====
    [New code to replace it with]
    >>>>
    """

    codebase_str = "\n".join([f"--- FILE: {f} ---\n{c}" for f, c in codebase.items()])
    ai_output = call_agent(system_prompt, f"CODE:\n{codebase_str}\n\nREQUEST: {prompt}", groq_key)

    if not ai_output: return
    
    # 3. SMART PARSING
    # Split by "File:" to process multiple files
    sections = re.split(r'File:\s*', ai_output)[1:]

    for section in sections:
        try:
            filename = section.split('\n')[0].strip()
            # Find SEARCH/REPLACE blocks
            blocks = re.findall(r'<{4,}\n(.*?)\n+={4,}\n(.*?)\n+>{4,}', section, re.DOTALL)
            
            if not blocks: continue
            
            if not os.path.exists(filename):
                # If creating new, the first block is the whole file
                with open(filename, "w") as f: f.write(blocks[0][1].strip())
                print(f"✅ Created: {filename}")
                continue

            with open(filename, "r") as f: content = f.read()
            
            for search_block, replace_block in blocks:
                search_block = search_block.strip('\n')
                replace_block = replace_block.strip('\n')
                
                # Remove Markdown backticks if AI added them
                replace_block = re.sub(r'^```[a-z]*\n|```$', '', replace_block, flags=re.MULTILINE).strip()

                match = fuzzy_find(search_block, content)
                
                if match:
                    content = content.replace(match, replace_block)
                    print(f"✅ Surgical patch applied to {filename}")
                else:
                    print(f"❌ Failed to find block in {filename}. AI provided incorrect anchor.")
            
            with open(filename, "w") as f: f.write(content)

        except Exception as e:
            print(f"❌ Error patching {filename}: {e}")

if __name__ == "__main__":
    run()
