import os, json, requests

groq_key = os.environ.get("GROQ_API_KEY")
file_path = os.environ.get("FILE_PATH")
prompt = os.environ.get("PROMPT")

with open(file_path, "r") as f:
    original_code = f.read()

lines = original_code.split('\n')
numbered_code = '\n'.join([f"{i+1}: {line}" for i, line in enumerate(lines)])

system_prompt = f"You are an expert AI. File with lines:\n{numbered_code}\nOutput ONLY a JSON object with 'start_line', 'end_line', and 'new_code'."

response = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
    json={
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
        "temperature": 0.1
    }
)

ai_output = response.json()["choices"][0]["message"]["content"]
ai_output = ai_output.replace("```json", "").replace("```", "").strip()
changes = json.loads(ai_output)

lines[changes["start_line"] - 1 : changes["end_line"]] = [changes["new_code"]]

with open(file_path, "w") as f:
    f.write('\n'.join(lines))
