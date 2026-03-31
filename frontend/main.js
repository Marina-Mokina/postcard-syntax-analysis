const btn = document.getElementById('analyze-button');
const input = document.getElementById('text-input');
const output = document.getElementById('text-output');
const modeRadios = document.getElementsByName('mode');

btn.addEventListener('click', async function() {
    const inputText = input.value.trim();
    if (!inputText) {
        alert('Пожалуйста, введите текст');
        return;
    }

    let mode = 'simple';
    for (let radio of modeRadios) {
        if (radio.checked) {
            mode = radio.value;
            break;
        }
    }

    btn.disabled = true;
    btn.textContent = 'Анализ...';

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: inputText, mode: mode })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка сервера');
        }

        const data = await response.json();

        output.value = format(data);

        alert('Анализ завершён!');
    } catch (error) {
        output.value = '';
        alert('Ошибка: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Проанализировать';
    }
});

function format(data) {
    let result = '';
    for (let [key, value] of Object.entries(data)) {
        result += `${key}: ${value}\n`;
    }
    return result;
}
