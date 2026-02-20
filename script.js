let mediaRecorder;
let audioChunks = [];
let timerInterval;
let startTime;

const btnStart = document.getElementById('btnRecord');
const btnStop = document.getElementById('btnStop');
const statusText = document.getElementById('statusText');
const timer = document.getElementById('timer');
const audioPlayback = document.getElementById('audioPlayback');
const logArea = document.getElementById('logArea');

btnStart.addEventListener('click', async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        
        audioChunks = []; // Reset chunks

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            const audioUrl = URL.createObjectURL(audioBlob);
            audioPlayback.src = audioUrl;
            
            // Upload to server
            logArea.innerHTML = "Uploading...";
            const formData = new FormData();
            formData.append('audio', audioBlob, 'lecture.webm');

            fetch('/upload', { 
                method: 'POST', 
                body: formData 
            })
            .then(res => res.json())
            .then(data => {
                logArea.innerHTML = `✅ Saved: ${data.filename}`;
            })
            .catch(err => {
                logArea.innerHTML = "❌ Upload Failed";
                console.error(err);
            });
        };

        mediaRecorder.start();
        
        // UI Updates
        btnStart.disabled = true;
        btnStop.disabled = false;
        statusText.innerText = "Recording...";
        startTime = Date.now();
        timerInterval = setInterval(updateTimer, 1000);
        
    } catch (err) {
        console.error("Error:", err);
        alert("Could not access microphone.");
    }
});

btnStop.addEventListener('click', () => {
    mediaRecorder.stop();
    btnStart.disabled = false;
    btnStop.disabled = true;
    statusText.innerText = "Ready";
    clearInterval(timerInterval);
});

function updateTimer() {
    const diff = Date.now() - startTime;
    const date = new Date(diff);
    timer.innerText = date.toISOString().substr(11, 8);
}