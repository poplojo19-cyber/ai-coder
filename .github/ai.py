import os, json, requests, re

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    file_path = os.environ.get("FILE_PATH")
    prompt = os.environ.get("PROMPT")

    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return

    with open(file_path, "r") as f:
        original_code = f.read()

    lines = original_code.split('\n')
    numbered_code = '\n'.join([f"{i+1}: {line}" for i, line in enumerate(lines)])

    system_prompt = "You are a coding tool. You MUST return ONLY a JSON object. No conversation."
    user_msg = f"In the file below, {prompt}\n\nFile:\n{numbered_code}\n\nReturn JSON: {{\"start_line\": int, \"end_line\": int, \"new_code\": str}}"

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            "temperature": 0.1
        }
    )

    if not resp.ok:
        print(f"API Error: {resp.text}")
        return

    full_content = resp.json()["choices"][0]["message"]["content"]
    
    try:
        json_match = re.search(r'\{.*\}', full_content, re.DOTALL)
        if json_match:
            changes = json.loads(json_match.group())
            start = int(changes["start_line"]) - 1
            end = int(changes["end_line"])
            new_text = changes["new_code"]

            lines[start:end] = [new_text]

            with open(file_path, "w") as f:
                f.write('\n'.join(lines))
            print("Successfully updated file.")
        else:
            print("No JSON found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
