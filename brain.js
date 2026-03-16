// --- CONFIG ---
const GH_USER = "poplojo19-cyber"; const GH_REPO = "ai-coder"; const GH_TOKEN = "ghp_" + "WX43QWawqoTDF27wCCpKc5bl0siMAp01wsKH"; // Put your token here
// --------------

const logArea = document.getElementById('logArea');
const runBtn = document.getElementById('runBtn');

const logTerminal = (m) => { 
    logArea.innerHTML += `<div>> ${m}</div>`; 
    logArea.scrollTop = logArea.scrollHeight;
};

runBtn.onclick = async () => {
    const prompt = document.getElementById('promptInput').value;
    if (!prompt) return;

    runBtn.disabled = true;
    logTerminal("🚀 Sending command to GitHub...");

    try {
        const res = await fetch(`https://api.github.com/repos/${GH_USER}/${GH_REPO}/actions/workflows/ai.yml/dispatches`, {
            method: 'POST',
            headers: { 
                'Authorization': `token ${GH_TOKEN}`, 
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            },
            // NOTICE: No file_path here!
            body: JSON.stringify({ 
                ref: 'main', 
                inputs: { prompt: prompt } 
            })
        });

        if (res.ok) {
            logTerminal("✅ Success! AI is thinking...");
            document.getElementById('promptInput').value = "";
        } else {
            const err = await res.json();
            logTerminal(`❌ Error: ${err.message}`);
        }
    } catch (e) {
        logTerminal(`❌ Error: ${e.message}`);
    } finally {
        runBtn.disabled = false;
    }
};
