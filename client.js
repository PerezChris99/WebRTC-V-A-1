let pc = new RTCPeerConnection();

// Handle incoming stream tracks
pc.ontrack = event => {
    if (event.track.kind === 'video') {
        document.getElementById('remoteVideo').srcObject = event.streams[0];
    }
};

// Offer to receive video
async function start() {
    let offer = await fetch('/offer').then(r => r.json());
    await pc.setRemoteDescription(offer);
    let answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);

    let ws = new WebSocket('ws://localhost:8080/ws');
    ws.onmessage = async (event) => {
        let answer = JSON.parse(event.data);
        await pc.setRemoteDescription(answer);
    };
}

start();
