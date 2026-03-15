const GH_USER = "poplojo19-cyber";
const GH_REPO = "ai-coder";
const GH_TOKEN = "ghp_" + "WX43QWawqoTDF27wCCpKc5bl0siMAp01wsKH";

const logArea = document.getElementById('logArea');
const runBtn = document.getElementById('runBtn');

const logTerminal = (m) => { 
    logArea.innerHTML += `<div class="text-blue-400 font-mono text-xs mb-1">> ${m}</div>`; 
    logArea.scrollTop = logArea.scrollHeight;
};

runBtn.onclick = async () => {
    const prompt = document.getElementById('promptInput').value;
    if (!prompt) return;

    logTerminal("🚀 Sending request...");
    
    // Trigger the workflow
    const res = await fetch(`https://api.github.com/repos/${GH_USER}/${GH_REPO}/actions/workflows/ai.yml/dispatches`, {
        method: 'POST',
        headers: { 'Authorization': `token ${GH_TOKEN}`, 'Accept': 'application/vnd.github.v3+json' },
        body: JSON.stringify({ 
            ref: 'main', 
            inputs: { 
                prompt: prompt,
                file_path: "index.html" 
            } 
        })

    if (res.ok) {
        logTerminal("✅ Request sent! GitHub is processing.");
        logTerminal("Watching for results in 10s...");
        
        // This is a "Polling" loop - it checks GitHub to see if the job is done
        setTimeout(checkLogs, 10000);
    }
};

async function checkLogs() {
    logTerminal("🔍 Checking GitHub Action logs...");
    const res = await fetch(`https://api.github.com/repos/${GH_USER}/${GH_REPO}/actions/runs`, {
        headers: { 'Authorization': `token ${GH_TOKEN}` }
    });
    const data = await res.json();
    const lastRun = data.workflow_runs[0];
    
    if (lastRun.status === 'completed') {
        logTerminal(`🎉 Action completed: ${lastRun.conclusion}`);
        logTerminal("Refresh the page to see changes!");
    } else {
        logTerminal("⏳ Still working...");
        setTimeout(checkLogs, 5000);
    }
}
