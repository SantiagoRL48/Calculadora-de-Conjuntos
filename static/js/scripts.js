function calculate() {
    const set1 = document.getElementById('set1').value;
    const set2 = document.getElementById('set2').value;
    const set3 = document.getElementById('set3').value;
    let expression = document.getElementById('expression').value;
    const sortOutput = document.getElementById('sortOutput').checked;

    // Validar que la expresión tenga paréntesis balanceados
    let parenCount = 0;
    for (let char of expression) {
        if (char === '(') parenCount++;
        if (char === ')') parenCount--;
        if (parenCount < 0) {
            document.getElementById('result-text').innerText = 'Error';
            document.getElementById('result-note').innerText = 'Error: Paréntesis no balanceados';
            return;
        }
    }
    if (parenCount !== 0) {
        document.getElementById('result-text').innerText = 'Error';
        document.getElementById('result-note').innerText = 'Error: Paréntesis no balanceados';
        return;
    }

    fetch('/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ set1, set2, set3, expression, sortOutput }),
    })
    .then(response => response.json())
    .then(data => {
        const resultContainer = document.getElementById('result-container');
        const resultText = document.getElementById('result-text');
        const resultNote = document.getElementById('result-note');

        resultText.innerText = data.result;
        resultNote.innerText = data.isEmpty ? 'El conjunto resultante es vacío porque no hay elementos comunes.' : data.error || '';
        resultContainer.classList.add('highlight');

        setTimeout(() => resultContainer.classList.remove('highlight'), 1000);
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('result-text').innerText = 'Error al calcular';
    });
}

function sortSets() {
    const set1 = document.getElementById('set1');
    const set2 = document.getElementById('set2');
    const set3 = document.getElementById('set3');
    set1.value = set1.value.split(',').map(item => item.trim()).sort().join(',');
    set2.value = set2.value.split(',').map(item => item.trim()).sort().join(',');
    set3.value = set3.value.split(',').map(item => item.trim()).sort().join(',');
    calculate();
}

function swapSets() {
    const set1 = document.getElementById('set1');
    const set2 = document.getElementById('set2');
    const set3 = document.getElementById('set3');
    const temp = set1.value;
    set1.value = set2.value;
    set2.value = set3.value;
    set3.value = temp;
    calculate();
}

function generateRandomExample() {
    const numbers = Array.from({ length: 9 }, (_, i) => (i + 1).toString());
    const letters = ['a', 'b', 'c', 'd'];
    const allElements = [...numbers, ...letters];

    const set1 = new Set();
    const set2 = new Set();
    const set3 = new Set();

    const size1 = Math.floor(Math.random() * 3) + 3;
    const size2 = Math.floor(Math.random() * 3) + 3;
    const size3 = Math.floor(Math.random() * 3) + 3;

    while (set1.size < size1) set1.add(allElements[Math.floor(Math.random() * allElements.length)]);
    while (set2.size < size2) set2.add(allElements[Math.floor(Math.random() * allElements.length)]);
    while (set3.size < size3) set3.add(allElements[Math.floor(Math.random() * allElements.length)]);

    document.getElementById('set1').value = Array.from(set1).join(',');
    document.getElementById('set2').value = Array.from(set2).join(',');
    document.getElementById('set3').value = Array.from(set3).join(',');
    document.getElementById('expression').value = '(A ∩ B) ∩ C';
    calculate();
}

function loadExample() {
    generateRandomExample();
}

function exportResult() {
    const resultText = document.getElementById('result-text').innerText;
    navigator.clipboard.writeText(resultText)
        .then(() => alert('Resultado copiado al portapapeles: ' + resultText))
        .catch(err => console.error('Error al copiar: ', err));
}

function insertOperator(symbol) {
    console.log(`Insertando operador: ${symbol}`);
    const expressionInput = document.getElementById('expression');
    if (!expressionInput) {
        console.error('Campo de expresión no encontrado');
        return;
    }
    const start = expressionInput.selectionStart || 0;
    const end = expressionInput.selectionEnd || 0;
    const currentValue = expressionInput.value || '';
    const newValue = currentValue.substring(0, start) + ' ' + symbol + ' ' + currentValue.substring(end);
    expressionInput.value = newValue.trim();
    expressionInput.focus();
    const newPosition = start + symbol.length + 2;
    expressionInput.setSelectionRange(newPosition, newPosition);
    calculate();
}

window.onload = calculate;