const apiPath = `/${document.getElementById('apiPath').value}`
const subscriptionPassword = `/${document.getElementById('subscriptionPassword').value}`

// Graphics
const copySVG = `<svg xmlns="http://www.w3.org/2000/svg" height="20" width="20" viewBox="0 0 20 20" fill="#555">
<rect x="6" y="6" width="9" height="11" rx="2" stroke="#555" stroke-width="1.2" fill="none"/>
<rect x="3" y="3" width="9" height="11" rx="2" fill="none" stroke="#888" stroke-width="1"/></svg>
`;
const restartTunnelSVG = `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="36px" fill="#070"><path d="m653-208-88 88-85-85 88-88q-4-11-6-23t-2-24q0-58 41-99t99-41q18 0 35 4.5t32 12.5l-95 95 56 56 95-94q8 15 12.5 31.5T840-340q0 58-41 99t-99 41q-13 0-24.5-2t-22.5-6Zm178-352h-83q-26-88-99-144t-169-56q-117 0-198.5 81.5T200-480q0 72 32.5 132t87.5 98v-110h80v240H160v-80h94q-62-50-98-122.5T120-480q0-75 28.5-140.5t77-114q48.5-48.5 114-77T480-840q129 0 226.5 79.5T831-560Z"/></svg>`;

const stopTunnelSVG = `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="36px" fill="#700"><path d="m336-280 144-144 144 144 56-56-144-144 144-144-56-56-144 144-144-144-56 56 144 144-144 144 56 56ZM480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/></svg>`;

const qrSVG = `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px" fill="#333">
<path d="M3 11h8V3H3v8zm2-6h4v4H5V5zM3 21h8v-8H3v8zm2-6h4v4H5v-4zM13 3v8h8V3h-8zm6 6h-4V5h4v4zM19 13h2v2h-2zM13 13h2v2h-2zM15 15h2v2h-2zM13 17h2v2h-2zM15 19h2v2h-2zM17 17h2v2h-2zM17 13h2v2h-2zM19 15h2v2h-2zM19 19h2v2h-2z"/>
</svg>`;



// let apiPath = "/{{ api_path }}";
// let subscriptionPassword = "{{ subscription_password }}";

// Global variable to track progress bar interval
let pbarInterval = null;

function renderTunnels(tunnels) {
    let container = document.getElementById('tunnels');
    if (tunnels.length === 0) {
        container.innerHTML = '<p>No tunnels available.</p>';
        return;
    }
    container.innerHTML = ''; // Clear existing content
    tunnels.forEach(tunnel => {
        let card = document.createElement('div');
        card.className = 'card' + (tunnel.process ? '' : ' card-unavailable');
        card.innerHTML = `
            <p onclick="showInfo(${tunnel.id})" class="provider-name">${tunnel.provider_instance}</p>
            <div class="innergrid">
                <div class="copybox">
                    <a class="truncate" href="${tunnel.url}">${tunnel.url}</a>
                    <div class="copybtn">
                        <button title="Copy" onclick="copyText(event)">${copySVG}</button>
                    </div>
                </div>
                <div class="btn">
                    <button onclick="restartTunnel(${tunnel.id})">${restartTunnelSVG}</button>
                    <button onclick="stopTunnel(${tunnel.id})">${stopTunnelSVG}</button>
                    <button onclick="showInfo('${tunnel.id}')">${qrSVG}</button>
                </div>
            </div>
            <p class="truncate" style="padding: 0px 20px; margin:0px;font-size:0.8em;">${tunnel.public_url}</p>
        `;
        container.appendChild(card);
    });
    makeLinksUnclickable();
}

function renderProviders(providers) {
    let providerSection = document.getElementById('providers');
    providerSection.innerHTML = ''; // Clear existing content
    providers.forEach(provider => {
        let providerDiv = document.createElement('div');
        providerDiv.className = 'provider';
        providerDiv.innerHTML = `
            <input type="checkbox" id="provider${provider.id}" value="${provider.id}" onclick="updateProviderSelection(this)" ${provider.user_enabled ? 'checked' : ''} />
            <label for="provider${provider.id}">${provider.provider}</label>
        `;
        providerSection.appendChild(providerDiv);
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

function updateProviderSelection(checkbox) {
    let providerId = checkbox.value;
    // Toggle provider via API
    fetchwithPreload(apiPath + '/providers/' + providerId, 'POST', preload=false, kwargs={
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(data => {
            showToast(`${data.provider} is now set to ${data.user_enabled ? 'enabled' : 'disabled'}.`);
            // refresh providers
            getAllProviders();
        }
    )
}

function getAllTunnels() {
    fetchwithPreload(apiPath + '/tunnels', 'GET')
    .then(data => {
        renderTunnels(data);
    })
    .catch(error => {
        console.error('Error fetching tunnels:', error);
        showToast('Failed to fetch tunnels.');
    });
}

function restartTunnel(id) {
    fetchwithPreload(apiPath + '/tunnels/' + id, 'POST')
    .then(data => {
        let color = data.code === 'error' ? '#DE1A1A' : '#333'; 
        showToast(data.msg, color);
        getAllTunnels(); // Refresh the list
    })
    .catch(error => {
        console.error('API error.', error);
        showToast('API error.', '#DE1A1A');
    });
}

// https://www.w3schools.com/howto/howto_css_modals.asp
var modal = document.getElementById("myModal");

// Get the button that opens the modal
var btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

function cleanupModal() {
    modal.style.display = "none";
    if (pbarInterval) {
        clearInterval(pbarInterval);
        pbarInterval = null;
    }
}

// When the user clicks on <span> (x), close the modal
span.onclick = cleanupModal;

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    cleanupModal();
  }
} 

function renderQRCode(url) {
    modal.style.display = "block";
    qrcode.makeCode(url);
}

function showInfo(id) {
    modal.style.display = "block";
    
    // Clear any existing progress interval
    if (pbarInterval) {
        clearInterval(pbarInterval);
        pbarInterval = null;
    }
    
    fetchwithPreload(apiPath + '/tunnels/' + id, 'GET', false)
    .then(data => {
        // *1000 to convert to milliseconds
        startTime = data.tun_start_time ? new Date(data.tun_start_time*1000).toLocaleString() : "N/A";
        endTime = data.tun_end_time ? new Date(data.tun_end_time*1000).toLocaleString() : Infinity;
        renderQRCode(data.url);
        let infoContent = document.getElementById('infoContent');
        infoContent.innerHTML = `
            <div style="display: flex;">
                <h2>Provider: ${data.provider_instance}</h2>
                <div class="btn" style="flex-direction: row; margin-left: auto;">
                    <button onclick="restartTunnel(${id})">${restartTunnelSVG}</button>
                    <button onclick="stopTunnel(${id})">${stopTunnelSVG}</button>
                </div>
            </div>
            <p><strong>URL:</strong> <a href="${data.url}" target="_blank">${data.url}</a></p>
            <p><strong>Public URL:</strong> <a href="https://${data.public_url}" target="_blank">${data.public_url}</a></p>
            <p><strong>Status:</strong> ${data.process ? 'Running' : 'Stopped'}</p>
            <p><strong>Created At:</strong> ${startTime}</p>
            <p><strong>Expiry:</strong> ${endTime}</p>
            <div style="display:flex; gap: 5px;">
                <div id="myProgress">
                    <div id="myBar"></div>
                </div> 
                <button class="modalBtn" onclick="changeTunnelTimer(${id}, 0); cleanupModal();">Perma</button>
            </div>
            <div style="display:flex; gap: 5px;">
                <input type="range" id="expireInput" min="1" max="1440"  style="flex:1; padding:5px;"/>
                <p id="expireValue">Unknown</p>
                <button class="modalBtn" onclick="setExpireHandler(${id}); cleanupModal();">Set Expiry</button>
            </div>
        `;
        // Expire Input
        const expireInput = document.getElementById('expireInput');
        const expireValue = document.getElementById('expireValue');
    
        expireInput.addEventListener('input', function() {
            expireValue.textContent = `${this.value} min`;
        });
        
        // Start progress bar if we have valid start and end times
        if (data.tun_start_time && data.tun_end_time) {
            startProgressBar(data.tun_start_time * 1000, data.tun_end_time * 1000);
        }
    })
    .catch(error => {
        console.error('Error fetching tunnel info:', error);
        showToast('Failed to fetch tunnel info.', '#DE1A1A');
    });
}

function setExpireHandler(id) {
    const expireTime = document.getElementById('expireInput').value;
    const expireMinutes = parseInt(expireTime);
    changeTunnelTimer(id, expireMinutes);
}

function startProgressBar(startTimeMs, endTimeMs) {
    const progressBar = document.getElementById('myBar');
    
    if (!progressBar) return;
    
    function updateProgress() {
        const now = Date.now();
        const totalDuration = endTimeMs - startTimeMs;
        const elapsed = now - startTimeMs;
        const remaining = endTimeMs - now;
        
        // Calculate percentage (100% at start, 0% at expiry)
        let percentage;
        if (now < startTimeMs) {
            // Before start time
            percentage = 100;
        } else if (now >= endTimeMs) {
            // After expiry
            percentage = 0;
        } else {
            // During active period
            percentage = Math.max(0, ((endTimeMs - now) / totalDuration) * 100);
        }
        
        // Update progress bar
        progressBar.style.width = percentage + '%';
        
        // Update color
        if (percentage > 50) {
            progressBar.style.backgroundColor = '#4CAF50'; // Green
        } else if (percentage > 20) {
            progressBar.style.backgroundColor = '#FF9800'; // Orange
        } else {
            progressBar.style.backgroundColor = '#F44336'; // Red
        }

        if (!(remaining > 0)) {
            // Clear interval when expired
            cleanupModal();
        }

    }
    
    // Update immediately
    updateProgress();
    
    // Update every second
    pbarInterval = setInterval(updateProgress, 1000);
}


const qrcode = new QRCode(document.getElementById('qrcode'), {
    colorDark : '#000',
    colorLight : '#fff',
    correctLevel : QRCode.CorrectLevel.L
});    

function changeTunnelTimer(id, expire) {
    fetchwithPreload(apiPath + '/tunnels/' + id + '/timer', 'POST', preload=false, kwargs={
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ expire: expire }) // expire in seconds
    })
    .then(data => {
        let color = data.code === 'error' ? '#DE1A1A' : '#333';
        showToast(data.msg, color);
        getAllTunnels(); // Refresh the list
    })
    .catch(error => {
        console.error('API error.', error);
        showToast('API error.', '#DE1A1A');
    });
}

function restartAllTunnels(scope="all") {
    fetchwithPreload(apiPath + '/tunnels', 'POST', preload=false, kwargs={
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ providers: scope }) // Specify scope if needed
    })
    .then(data => {
        showToast('All tunnels restarted successfully.');
        getAllTunnels(); // Refresh the list
    })
    .catch(error => {
        console.error('API error.', error);
        showToast('API error.', '#DE1A1A');
    });
}

function stopTunnel(id) {
    fetchwithPreload(apiPath + '/tunnels/' + id, 'DELETE')
    .then(data => {
        showToast('Tunnel stopped successfully.');
        getAllTunnels(); // Refresh the list
    })
    .catch(error => {
        console.error('API error.', error);
        showToast('API error.', '#DE1A1A');
    });
}

function stopAllTunnels() {
    fetchwithPreload(apiPath + '/tunnels/all', 'DELETE', preload=false)
    .then(data => {
        showToast('All tunnels stopped successfully.');
        getAllTunnels(); // Refresh the list
    })
    .catch(error => {
        console.error('API error.', error);
        showToast('API error.', '#DE1A1A');
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

function copyText(event) {
    const text = event.target.closest('.copybox').querySelector('a').textContent;
    let thatCard = event.target.closest('.card');
    if (thatCard.classList.contains('card-unavailable')) {
        showToast('This tunnel is unavailable.');
        return;
    } else {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard!');
        }).catch(err => {
            alert('Failed to copy: ' + err);
        });
    }
}

function copyAll() {
    let allTunnels = fetch(subscriptionPassword + "/subscription")
        .then(response => response.text())
        .then(data => {
            navigator.clipboard.writeText(data).then(() => {
                showToast('All tunnels copied to clipboard!');
            }).catch(err => {
                alert('Failed to copy: ' + err);
            });
        })
        .catch(error => {
            console.error('Error fetching subscription:', error);
            showToast('Failed to fetch subscription.', '#DE1A1A');
        });
}

function showToast(message, color="#333") {
    // Remove existing toast if any, ensuring only one toast is visible at a time
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toast.style.backgroundColor = color; // Set background color
    toast.style.color = '#fff'; // Set text color for contrast
    document.body.appendChild(toast);

    // Fade out and remove the toast after a delay
    setTimeout(() => {
        toast.classList.add('hide'); // Add a class for fading out
        toast.addEventListener('transitionend', () => {
            toast.remove();
        }, { once: true }); // Remove after transition
    }, 3000);
}
// Make links unclickable
function makeLinksUnclickable() {
    let displayedLinks = document.querySelectorAll('a.truncate');
    displayedLinks.forEach(link => {
        link.onclick = function(e) {
            copyText(e);
            return e.preventDefault() && e.stopPropagation();
        };
    });
}

// Toggle show/hide functionality
function toggleShowHide() {
    let providerSection = document.getElementById('providers-toggles');
    providerSection.style.display = (providerSection.style.display === 'block' || providerSection.style.display === '') ? 'none' : 'block';
}
getAllTunnels(); // Initial fetch to populate tunnels
getAllProviders(); // Initial fetch to populate providers
document.getElementById('copySVG').innerHTML = copySVG; // Set the copy button SVG
