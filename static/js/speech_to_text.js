(() => {
    const dropZone = document.getElementById('dropZone');
    const audioFileInput = document.getElementById('audioFileInput');
    const fileMeta = document.getElementById('fileMeta');
    const fileNameEl = document.getElementById('selectedFileName');
    const fileSizeEl = document.getElementById('selectedFileSize');
    const inputModeButtons = document.getElementById('inputModeButtons');
    const uploadPanel = document.getElementById('uploadPanel');
    const recordPanel = document.getElementById('recordPanel');
    const recordToggle = document.getElementById('recordToggle');
    const recordTimer = document.getElementById('recordTimer');
    const recordHint = document.getElementById('recordHint');
    const processingState = document.getElementById('processingState');
    const processBtn = document.getElementById('processBtn');
    const resultSection = document.getElementById('resultSection');
    const resultCard = document.getElementById('resultCard');
    const resultTitle = document.getElementById('resultTitle');
    const resultText = document.getElementById('resultText');
    const translateSelect = document.getElementById('translateSelect');
    const copyTextBtn = document.getElementById('copyTextBtn');
    const metaDuration = document.getElementById('metaDuration');
    const metaWords = document.getElementById('metaWords');
    const errorAlert = document.getElementById('errorAlert');
    const successAlert = document.getElementById('successAlert');

    const state = {
        mode: 'upload',
        selectedFile: null,
        recordedBlob: null,
        mediaRecorder: null,
        recordingStream: null,
        timerInterval: null,
        startTime: null,
        transcript: '',
        translations: {},
    };

    function resetAlerts() {
        [errorAlert, successAlert].forEach(alert => {
            alert.classList.add('d-none');
            alert.textContent = '';
        });
    }

    function showAlert(target, message) {
        resetAlerts();
        target.textContent = message;
        target.classList.remove('d-none');
    }

    function formatBytes(bytes) {
        if (!bytes) return '0 B';
        const units = ['B', 'KB', 'MB', 'GB'];
        const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
        const value = bytes / Math.pow(1024, exponent);
        return `${value.toFixed(exponent === 0 ? 0 : 2)} ${units[exponent]}`;
    }

    function setMode(mode) {
        if (state.mode === mode) return;
        state.mode = mode;
        inputModeButtons.querySelectorAll('button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });
        if (mode === 'upload') {
            uploadPanel.classList.remove('d-none');
            recordPanel.classList.add('d-none');
            processBtn.disabled = !state.selectedFile;
        } else {
            recordPanel.classList.remove('d-none');
            uploadPanel.classList.add('d-none');
            processBtn.disabled = !state.recordedBlob;
        }
    }

    function handleFile(file) {
        if (!file) return;
        state.selectedFile = file;
        fileMeta.classList.remove('d-none');
        fileNameEl.textContent = file.name;
        fileSizeEl.textContent = formatBytes(file.size);
        processBtn.disabled = false;
    }

    function clearFileSelection() {
        state.selectedFile = null;
        audioFileInput.value = '';
        fileMeta.classList.add('d-none');
        processBtn.disabled = true;
    }

    function startRecording() {
        if (state.mediaRecorder && state.mediaRecorder.state === 'recording') return;

        navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
            state.recordingStream = stream;
            state.mediaRecorder = new MediaRecorder(stream);
            const chunks = [];

            state.mediaRecorder.ondataavailable = evt => {
                if (evt.data && evt.data.size > 0) {
                    chunks.push(evt.data);
                }
            };

            state.mediaRecorder.onstop = () => {
                if (state.recordingStream) {
                    state.recordingStream.getTracks().forEach(track => track.stop());
                    state.recordingStream = null;
                }
                state.recordedBlob = new Blob(chunks, { type: 'audio/webm' });
                processBtn.disabled = false;
                recordHint.textContent = 'Recording saved! Click Process to transcribe.';
                recordHint.classList.remove('text-danger');
                recordHint.classList.add('text-success');
            };

            recordHint.textContent = 'Recording in progress… tap to stop.';
            recordHint.classList.remove('text-success');
            recordHint.classList.add('text-danger');
            recordToggle.classList.add('recording');
            state.recordedBlob = null;
            processBtn.disabled = true;

            state.mediaRecorder.start();
            state.startTime = Date.now();
            recordTimer.textContent = '00:00';
            state.timerInterval = setInterval(() => {
                const elapsed = Math.floor((Date.now() - state.startTime) / 1000);
                const minutes = String(Math.floor(elapsed / 60)).padStart(2, '0');
                const seconds = String(elapsed % 60).padStart(2, '0');
                recordTimer.textContent = `${minutes}:${seconds}`;
                if (elapsed >= 120) {
                    showAlert(errorAlert, 'Maximum recording duration (2 minutes) reached.');
                    stopRecording();
                }
            }, 1000);
        }).catch(() => {
            showAlert(errorAlert, 'Microphone access denied. Please enable microphone permissions.');
        });
    }

    function stopRecording() {
        if (state.timerInterval) {
            clearInterval(state.timerInterval);
            state.timerInterval = null;
        }
        if (state.mediaRecorder && state.mediaRecorder.state === 'recording') {
            state.mediaRecorder.stop();
        }
        recordToggle.classList.remove('recording');
    }

    function setProcessing(isProcessing) {
        if (isProcessing) {
            processingState.classList.remove('d-none');
            processBtn.disabled = true;
        } else {
            processingState.classList.add('d-none');
            processBtn.disabled = state.mode === 'upload' ? !state.selectedFile : !state.recordedBlob;
        }
    }

    function resetResults() {
        state.transcript = '';
        state.translations = {};
        resultCard.classList.remove('show');
        resultText.textContent = '';
        translateSelect.value = 'original';
        resultTitle.textContent = 'Transcript (English)';
        metaDuration.textContent = '0s';
        metaWords.textContent = '0 words';
    }

    function updateResult(text, durationSeconds) {
        resultText.textContent = text;
        resultTitle.textContent = translateSelect.value === 'original' ? 'Transcript (English)' : `Translation (${translateSelect.options[translateSelect.selectedIndex].text})`;
        metaDuration.textContent = `${durationSeconds}s`;
        const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
        metaWords.textContent = `${wordCount} ${wordCount === 1 ? 'word' : 'words'}`;
        resultCard.classList.add('show');
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function handleProcess() {
        resetAlerts();
        resetResults();
        setProcessing(true);

        if (state.mode === 'upload' && state.selectedFile) {
            const formData = new FormData();
            formData.append('audio_file', state.selectedFile);
            fetch('/process-audio', { method: 'POST', body: formData })
                .then(resp => resp.json())
                .then(handleProcessResponse)
                .catch(() => showAlert(errorAlert, 'Network error. Please try again.'))
                .finally(() => setProcessing(false));
        } else if (state.mode === 'record' && state.recordedBlob) {
            const reader = new FileReader();
            reader.onloadend = () => {
                const payload = { audio_data: reader.result };
                fetch('/process-audio', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                })
                    .then(resp => resp.json())
                    .then(handleProcessResponse)
                    .catch(() => showAlert(errorAlert, 'Network error. Please try again.'))
                    .finally(() => setProcessing(false));
            };
            reader.readAsDataURL(state.recordedBlob);
        } else {
            setProcessing(false);
            showAlert(errorAlert, 'Nothing to process. Please upload a file or record audio.');
        }
    }

    function handleProcessResponse(result) {
        if (!result || !result.success) {
            showAlert(errorAlert, result?.message || 'Processing failed. Please try again.');
            return;
        }

        state.transcript = result.original_text || '';
        state.translations = { ...result.translations };
        state.translations.original = state.transcript;
        translateSelect.value = 'original';
        updateResult(state.transcript, (result.duration ?? 0).toFixed(2));
        showAlert(successAlert, 'Audio processed successfully!');
    }

    function handleTranslationChange() {
        const selected = translateSelect.value;
        if (!state.transcript) {
            translateSelect.value = 'original';
            return;
        }

        if (state.translations[selected]) {
            updateResult(state.translations[selected], metaDuration.textContent.replace('s', ''));
            return;
        }

        setProcessing(true);
        fetch('/translate-text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: state.transcript, language: selected })
        })
            .then(resp => resp.json())
            .then(data => {
                if (!data || !data.success) {
                    translateSelect.value = 'original';
                    showAlert(errorAlert, data?.message || 'Translation failed.');
                    updateResult(state.transcript, metaDuration.textContent.replace('s', ''));
                    return;
                }
                state.translations[selected] = data.translated_text;
                updateResult(data.translated_text, metaDuration.textContent.replace('s', ''));
            })
            .catch(() => {
                translateSelect.value = 'original';
                showAlert(errorAlert, 'Network error while translating.');
                updateResult(state.transcript, metaDuration.textContent.replace('s', ''));
            })
            .finally(() => setProcessing(false));
    }

    function handleCopy() {
        if (!resultText.textContent) return;
        navigator.clipboard.writeText(resultText.textContent.trim()).then(() => {
            copyTextBtn.classList.add('copied');
            copyTextBtn.innerHTML = '<i class="bi bi-clipboard-check"></i>';
            setTimeout(() => {
                copyTextBtn.classList.remove('copied');
                copyTextBtn.innerHTML = '<i class="bi bi-clipboard"></i>';
            }, 2000);
        });
    }

    // Event wiring
    inputModeButtons.addEventListener('click', evt => {
        const btn = evt.target.closest('button[data-mode]');
        if (!btn) return;
        setMode(btn.dataset.mode);
        resetAlerts();
    });

    dropZone.addEventListener('click', () => audioFileInput.click());
    dropZone.addEventListener('dragover', evt => {
        evt.preventDefault();
        dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', evt => {
        evt.preventDefault();
        dropZone.classList.remove('dragover');
        const file = evt.dataTransfer.files?.[0];
        if (file) {
            handleFile(file);
        }
    });

    audioFileInput.addEventListener('change', evt => {
        const file = evt.target.files?.[0];
        if (file) {
            handleFile(file);
        } else {
            clearFileSelection();
        }
    });

    recordToggle.addEventListener('click', () => {
        if (state.mediaRecorder && state.mediaRecorder.state === 'recording') {
            stopRecording();
        } else {
            startRecording();
        }
    });

    processBtn.addEventListener('click', handleProcess);
    translateSelect.addEventListener('change', handleTranslationChange);
    copyTextBtn.addEventListener('click', handleCopy);

    // Initial state
    setMode('upload');
    resetResults();
})();
