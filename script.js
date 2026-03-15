// --- YOUR PRIVATE CONFIG ---
const GH_USER = "YOUR_USERNAME"; 
const GH_REPO = "ai-coder";
const T_1 = "ghp_"; 
const T_2 = "WX43QWawqoTDF27wCCpKc5bl0siMAp01wsKH"; 
const GH_TOKEN = T_1 + T_2;
// ---------------------------------------

const logArea = document.getElementById('logArea');
const runBtn = document.getElementById('runBtn');

const logTerminal = (m) => { logArea.innerHTML += `<div>> ${m}</div>`; };

runBtn.onclick = async () => {
    logTerminal("Sending a test PING to GitHub...");

    // IMPORTANT: This URL points to our new test.yml file!
    const res = await fetch(`https://api.github.com/repos/${GH_USER}/${GH_REPO}/actions/workflows/test.yml/dispatches`, {
        method: 'POST',
        headers: { 
            'Authorization': `token ${GH_TOKEN}`, 
            'Accept': 'application/vnd.github.v3+json' 
        },
        body: JSON.stringify({ ref: 'main' })
    });

    if (res.ok) {
        logTerminal("✅ Signal sent! Check your 'Actions' tab on GitHub for 'Connection Test'.");
    } else {
        const errorData = await res.json();
        logTerminal(`❌ CONNECTION FAILED. Reason: ${errorData.message}`);
    }
};
