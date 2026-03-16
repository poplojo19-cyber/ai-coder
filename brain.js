const GH_USER = "poplojo19-cyber";
const GH_REPO = "ai-coder";
const GH_TOKEN = "ghp_" + "WX43QWawqoTDF27wCCpKc5bl0siMAp01wsKH"; // Put your token here

document.getElementById('runBtn').onclick = async () => {
    const prompt = document.getElementById('promptInput').value;
    const logArea = document.getElementById('logArea');
    
    if (!prompt) {
        alert("Please enter a prompt!");
        return;
    }

    logArea.innerHTML += "<div>> Sending request to GitHub...</div>";

    try {
        const response = await fetch(`https://api.github.com/repos/${GH_USER}/${GH_REPO}/actions/workflows/ai.yml/dispatches`, {
            method: 'POST',
            headers: { 
                'Authorization': `token ${GH_TOKEN}`, 
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                ref: 'main', 
                inputs: { 
                    prompt: prompt,
                    file_path: 'index.html' 
                } 
            })
        });

        if (response.ok) {
            logArea.innerHTML += "<div>> ✅ Success! Check the Actions tab.</div>";
        } else {
            const error = await response.text();
            logArea.innerHTML += `<div>> ❌ Error: ${error}</div>`;
        }
    } catch (err) {
        logArea.innerHTML += `<div>> ❌ Crash: ${err.message}</div>`;
    }
};
