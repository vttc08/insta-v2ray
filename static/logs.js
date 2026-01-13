const apiPath = `/${document.getElementById('apiPath').value}`

let allProviders = [];
const errorLevels = ["error", "warning", "info"];

function renderProviders(providersData) {
    let providerSection = document.getElementById('providers');
    providerSection.innerHTML = ''; // Clear existing content
    allProviders = []; // Reset the global array
    providersData.forEach(provider => {
        let providerDiv = document.createElement('div');
        providerDiv.className = 'provider';
        providerDiv.innerHTML = `
            <input type="checkbox" id="provider${provider.id}" value="${provider.provider}" onchange="updateProviderSelection(this)" checked />
            <label for="provider${provider.id}">${provider.provider}</label>
        `;
        providerSection.appendChild(providerDiv);
        allProviders.push(provider.provider.toLowerCase());
    });
}

function getAllProviders() {
    fetchwithPreload(apiPath + '/providers', 'GET')
    .then(data => {
        renderProviders(data);
        // Render providers if needed
    })
    .catch(error => {
        console.error('Error fetching providers:', error);
        showToast('Failed to fetch providers.');
    });
}

function fetchwithPreload(url, method='GET', preload=true, kwargs={}) {
    let preloadEl = document.querySelector('.preload');
    if (preload) {
        preloadEl.style.display = 'block'; // Show preload
    }
    return fetch(url, { method, ...kwargs })
        .then(response => {
            return response.json();
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            showToast('Failed to fetch data.', '#DE1A1A');
        })
        .finally(() => {
            if (preload) {
                preloadEl.style.display = 'none'; 
            }
        });
}

function showToast(message, color="#333") {
    // Remove existing toast if any
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toast.style.backgroundColor = color;
    toast.style.color = '#fff';
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.padding = '10px';
    toast.style.borderRadius = '5px';
    toast.style.zIndex = '9999';
    document.body.appendChild(toast);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function updateProviderSelection(checkbox) {
    renderLogs(filterLogs());
}

function updateErrorLevelSelection(checkbox) {
    renderLogs(filterLogs());
}

function checkEnabled() {
    let providerSection = document.getElementById('providers');
    let checkboxes = providerSection.querySelectorAll('input[type="checkbox"]');
    let selectedProviders = Array.from(checkboxes).filter(checkbox => checkbox.checked).map(checkbox => checkbox.value.toLowerCase());
    let errorLevelSection = document.getElementById('error-levels');
    let levelCheckboxes = errorLevelSection.querySelectorAll('input[type="checkbox"]');
    let selectedLevels = Array.from(levelCheckboxes).filter(checkbox => checkbox.checked).map(checkbox => checkbox.value.toLowerCase());
    return { selectedProviders, selectedLevels };
}


let content;

function filterLogs() {
    let { selectedProviders, selectedLevels } = checkEnabled();
    
    if (!content || content.length === 0) return [];
    
    return content.filter(log => {
        const logLower = log.toLowerCase();
        
        // If none selected, show everything
        const providerMatch = selectedProviders.length === 0 || selectedProviders.some(provider => logLower.includes(provider));
        const levelMatch = selectedLevels.length === 0 || selectedLevels.some(level => logLower.includes(level));
        
        return providerMatch && levelMatch;
    });
}
async function showAll() {
    content = await fetch("all", { method: 'GET' , headers: { 'Accept': 'application/json' }});
    content = await content.json();
    renderLogs(content.reverse());
}

function renderLogs(logs) {
    const errorColor = '#ff0019e8';
    const warningColor = '#dc8f00';
    let logSection = document.getElementById('log-entries');
    logSection.innerHTML = ''; // Clear existing content
    
    if (logs.length === 0) {
        logSection.innerHTML = '<p class="no-logs">No logs match the current filters.</p>';
        return;
    }
    
    logs.forEach(log => {
        color = log.toLowerCase().includes('error') ? errorColor :
                log.toLowerCase().includes('warning') ? warningColor : '#000';
        let logDiv = document.createElement('div');
        logDiv.className = 'log-entry';
        logDiv.innerHTML = `<p style="color:${color};">${log}</p><hr>`;
        logSection.appendChild(logDiv);
    });
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Set all error level checkboxes as checked by default
    errorLevels.forEach(level => {
        const checkbox = document.getElementById(level);
        if (checkbox) checkbox.checked = true;
    });
    
    // Load data
    showAll().then(() => {
        getAllProviders();
        // Initial render with all filters enabled
        setTimeout(() => renderLogs(filterLogs()), 100);
    });
});
