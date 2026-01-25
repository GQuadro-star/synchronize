document.addEventListener('DOMContentLoaded', () => {
    let pyodide;
    let lastResult = null;

    async function initPyodide() {
        if (!pyodide) {
            updateStatus('info', 'Загружаю Pyodide...');
            try {
                pyodide = await loadPyodide({
                    indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.23.4/full/'
                });
                await pyodide.loadPackage("micropip");
                const micropip = pyodide.pyimport("micropip");
                await micropip.install("cryptography");
                updateStatus('success', 'Pyodide готов');
            } catch (err) {
                console.error('Ошибка загрузки Pyodide:', err);
                updateStatus('danger', 'Ошибка загрузки Pyodide: ' + err.message);
                throw err;
            }
        }
    }

    function updateStatus(type, message) {
        const el = document.getElementById('status');
        el.textContent = message;
        el.className = `mt-3 alert alert-${type}`;

        if (document.documentElement.getAttribute('data-bs-theme') === 'dark') {
            el.style.color = '#e0e0e0';
            if (type === 'secondary') el.style.backgroundColor = '#2d2d2d';
            if (type === 'success') el.style.backgroundColor = '#1a3d1a';
            if (type === 'info') el.style.backgroundColor = '#1a2e3d';
            if (type === 'warning') el.style.backgroundColor = '#3d3d1a';
            if (type === 'danger') el.style.backgroundColor = '#3d1a1a';
        }
    }

    async function readFileAsDataURL(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onerror = () => reject(new Error('Ошибка чтения файла.'));
            reader.onload = () => resolve(reader.result.split(',')[1]);
            reader.readAsDataURL(file);
        });
    }

    function b64toBlob(b64Data, contentType = '') {
        const byteCharacters = atob(b64Data);
        const byteArrays = [];
        for (let offset = 0; offset < byteCharacters.length; offset += 512) {
            const slice = byteCharacters.slice(offset, offset + 512);
            const byteNumbers = new Array(slice.length);
            for (let i = 0; i < slice.length; i++) {
                byteNumbers[i] = slice.charCodeAt(i);
            }
            byteArrays.push(new Uint8Array(byteNumbers));
        }
        return new Blob(byteArrays, { type: contentType });
    }

    function getCsrfToken() {
        const csrfCookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        if (csrfCookie) {
            return csrfCookie.split('=')[1];
        }

        const csrfElement = document.querySelector('meta[name="csrf-token"]');
        if (csrfElement) {
            return csrfElement.getAttribute('content');
        }

        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) {
            return csrfInput.value;
        }

        return '';
    }

    function downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 0);
    }

    // Инициализация обработчиков
    document.getElementById('local-form').addEventListener('submit', async (ev) => {
        ev.preventDefault();
        const fileInput = document.getElementById('local-file');
        const keyInput = document.getElementById('encryption-key');
        const mode = document.querySelector('input[name="mode"]:checked').value;
        const outputEl = document.getElementById('output');
        const downloadBtn = document.getElementById('download-btn');
        const sendBtn = document.getElementById('send-btn');

        outputEl.textContent = '';
        downloadBtn.style.display = 'none';
        sendBtn.style.display = 'none';

        if (!fileInput.files[0]) return updateStatus('danger', 'Выберите файл');
        if (keyInput.value.length < 8) return updateStatus('danger', 'Ключ должен быть минимум 8 символов');

        try {
            updateStatus('warning', 'Читаю файл...');
            const file = fileInput.files[0];
            const b64data = await readFileAsDataURL(file);

            await initPyodide();

            updateStatus('info', 'Загружаю модуль шифрования...');
            const encryptPyCode = await (await fetch(window.ENCRYPT_PY_URL)).text();
            await pyodide.runPythonAsync(encryptPyCode);

            pyodide.globals.set('b64data', b64data);

            updateStatus('info', mode === 'encrypt' ? 'Шифрую...' : 'Расшифровываю...');
            const resultDict = pyodide
                .runPython(`
process_file(
  b64data,
  ${JSON.stringify(file.name)},
  ${JSON.stringify(file.type)},
  ${JSON.stringify(keyInput.value.trim())},
  ${JSON.stringify(mode)}
)
        `)
                .toJs();

            lastResult = {
                b64: resultDict.get('result_b64'),
                filename: resultDict.get('result_filename'),
                mime: resultDict.get('result_mime'),
                mode: resultDict.get('mode')
            };

            const size = Math.round((lastResult.b64.length * 3) / 4);
            outputEl.textContent = `✅ Успешно обработано!\n\nИмя: ${lastResult.filename}\nMIME: ${lastResult.mime}\nРазмер: ${size} байт`;

            updateStatus('success', 'Готово! Выберите действие с результатом');
            downloadBtn.style.display = 'inline-block';
            sendBtn.style.display = 'inline-block';

        } catch (err) {
            console.error(err);
            updateStatus('danger', `Ошибка: ${err.message || err}`);
        } finally {
            pyodide?.globals.delete('b64data');
        }
    });

    document.getElementById('download-btn').addEventListener('click', () => {
        if (!lastResult) return updateStatus('warning', 'Сначала обработайте файл');

        try {
            const { b64, filename, mime } = lastResult;
            const blob = b64toBlob(b64, mime);
            downloadBlob(blob, filename);
            updateStatus('success', `Файл "${filename}" сохранён на устройстве`);
        } catch (err) {
            console.error(err);
            updateStatus('danger', `Ошибка скачивания: ${err.message || err}`);
        }
    });

    document.getElementById('send-btn').addEventListener('click', async () => {
        if (!lastResult) return updateStatus('warning', 'Сначала обработайте файл');

        try {
            const { b64, filename, mime, mode } = lastResult;
            const blob = b64toBlob(b64, mime);
            const formData = new FormData();
            formData.append('file', blob, filename);

            updateStatus('info', 'Отправляю на сервер...');

            // Получаем CSRF токен
            const csrfToken = getCsrfToken();

            const response = await fetch('/upload/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            const result = await response.json();
            const downloadLink = `${window.location.origin}${result.download_url}`;

            let outputText = `✅ Файл успешно загружен на сервер\n`;
            outputText += `📁 Имя: ${result.filename}\n`;
            outputText += `🔗 Ссылка для скачивания: <a href="${downloadLink}" target="_blank">${downloadLink}</a>\n`;
            outputText += `💡 Вы можете скачать файл по этой ссылке или поделиться ею`;

            document.getElementById('output').innerHTML = outputText;
            updateStatus('success', 'Файл успешно загружен! Ссылка для скачивания доступна ниже');

            // Добавляем кнопку для перехода на страницу скачивания
            const downloadPageBtn = document.createElement('button');
            downloadPageBtn.className = 'btn btn-success mt-3';
            downloadPageBtn.innerHTML = 'Перейти на страницу скачивания';
            downloadPageBtn.onclick = () => window.location.href = downloadLink;

            document.querySelector('.base').appendChild(downloadPageBtn);

        } catch (err) {
            console.error('Ошибка отправки:', err);
            updateStatus('danger', `Ошибка отправки: ${err.message || err}`);
        }
    });
})