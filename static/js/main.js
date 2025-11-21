var ws = null;

function connect() {
    var username = document.getElementById('username').value.trim();
    if (!username) {
        alert('Enter a username');
        return;
    }

    if (ws) {
        ws.close();
    }

    ws = new WebSocket(`ws://${location.hostname}:8000/ws/${encodeURIComponent(username)}`);

    ws.onopen = function() {
        document.getElementById('status').textContent = 'Connected as ' + username;
        document.getElementById('connectBtn').disabled = true;
    };

    ws.onmessage = function(event) {
        var messages = document.getElementById('messages')
        var message = document.createElement('div')
        message.classList.add('alert', 'alert-info');
        var content = document.createTextNode(event.data)
        message.appendChild(content)
        messages.appendChild(message)
        messages.scrollTop = messages.scrollHeight;
    };

    ws.onclose = function() {
        document.getElementById('status').textContent = 'Disconnected';
        document.getElementById('connectBtn').disabled = false;
    };

    ws.onerror = function(e) {
        console.error('WebSocket error', e);
    };
}

function sendMessage() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert('Not connected');
        return;
    }
    var input = document.getElementById("messageText")
    var recipient = document.getElementById('recipient').value.trim();
    var payload = { to: recipient || null, message: input.value }
    ws.send(JSON.stringify(payload));
    input.value = ''
}

// Auto-connect if `user` query param is present (useful for demo/testing)
document.addEventListener('DOMContentLoaded', function() {
    try {
        var params = new URLSearchParams(window.location.search);
        var user = params.get('user');
        var recipient = params.get('to');
        var autoMsg = params.get('msg');
        if (user) {
            document.getElementById('username').value = user;
            if (recipient) document.getElementById('recipient').value = recipient;
            connect();
            if (autoMsg) {
                // send after short delay to ensure websocket open
                setTimeout(function() {
                    document.getElementById('messageText').value = autoMsg;
                    sendMessage();
                }, 400);
            }
        }
    } catch (e) {
        console.error('Auto-connect error', e);
    }
});
