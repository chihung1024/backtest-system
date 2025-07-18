// api.js: 處理對後端 API 的所有請求

const API_BASE_URL = '/api';

async function post(endpoint, body) {
    const url = `${API_BASE_URL}${endpoint}`;
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            // Try to parse error from backend, otherwise throw generic error
            try {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            } catch (e) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
        }
        return await response.json();
    } catch (error) {
        console.error(`API call to ${url} failed:`, error);
        throw error;
    }
}

export function runBacktest(payload) {
    return post('/backtest', payload);
}

export function runScan(payload) {
    return post('/scan', payload);
}
