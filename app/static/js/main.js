const statsContainer = document.getElementById('stats-container');

async function getData(url, method, data = null) {
    const response = await fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data || {}),
    });
    return response;
}

function parseTSV(tsv) {
    const rows = tsv.split('\n').map(row => row.split('\t'));
    return rows;
}

function displayData(data) {
    if (!data || data.length === 0) {
        statsContainer.innerHTML = '<p>Данных нет.</p>';
        return;
    }
    const parsedData = parseTSV(data.data);
    const tableHTML = `<table border="1">
                        ${parsedData.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`).join('')}
                      </table>`;
    statsContainer.innerHTML = tableHTML;
}

async function getTsvData(url, method, data) {
    const maxRetries = 3;
    const retryInterval = 5000;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        const response = await getData(url, method, data);

        if (response.status === 200) {
            const responseData = await response.json();
            displayData(responseData);
            break;
        } else if (attempt < maxRetries) {
            statsContainer.innerHTML = '<p>Ожидайте, получения данных...</p>';
            await new Promise(resolve => setTimeout(resolve, retryInterval));
        } else {
            console.error('Max retries reached. Unable to get a successful response.');
        }
    }
}

async function getStatistics() {
    const report_name = generateReportName();
    const data = { report_name };
    await getTsvData('/api/yandex/account-statistic', 'POST', data);
}

async function getKeywords() {
    const report_name = generateReportName();
    const data = { report_name };
    await getTsvData('/api/yandex/search-queries', 'POST', data);
}

async function getNegativeWords() {
    const response = await getData('/api/yandex/negative-keywords', 'POST', {});
    const responseData = await response.json();
    if (!responseData || !responseData.data || responseData.data.length === 0) {
        statsContainer.innerHTML = '<p>Данных нет.</p>';
        return;
    }
    statsContainer.innerHTML = responseData.data.join(', ');
}

function generateReportName() {
    const characters = 'abcdefghijklmnopqrstuvwxyz0123456789';
    const length = 8;
    let result = '';

    for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * characters.length);
        result += characters.charAt(randomIndex);
    }

    return result;
}
