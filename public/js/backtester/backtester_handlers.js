// backtester_handlers.js: 處理回測頁面的事件

import { dom } from '../dom.js';
import { state, updateState } from '../state.js';
import { renderChart, renderSummaryTable, displayError } from '../ui.js';
import { runBacktest } from '../api.js';
import { calculateMetrics } from '../utils.js';

export function setupBacktesterEventHandlers() {
    if (dom.runBacktestBtn) {
        dom.runBacktestBtn.addEventListener('click', handleRunBacktest);
    }
}

async function handleRunBacktest() {
    const tickers = dom.tickersTextarea.value.split('\n').map(t => t.trim()).filter(t => t);
    if (tickers.length === 0) {
        alert('請輸入至少一個股票代碼');
        return;
    }

    const payload = {
        tickers: tickers,
        start: `${dom.backtestStartYear.value}-${dom.backtestStartMonth.value}-01`,
        end: `${dom.backtestEndYear.value}-${dom.backtestEndMonth.value}-28` // Use 28 to be safe
    };

    dom.runBacktestBtn.disabled = true;
    dom.runBacktestBtn.textContent = '回測執行中...';

    try {
        const result = await runBacktest(payload);
        
        if (result.error) {
            displayError(dom.chartContainer, result.error);
            renderSummaryTable([], null); // Clear summary table
            return;
        }

        const equityData = JSON.parse(result.equity);
        const portfolioHistory = Object.entries(equityData).map(([date, value]) => ({ date, value }));

        const portfolio = {
            name: '投資組合',
            cagr: result.cagr,
            mdd: result.mdd,
            sharpe_ratio: result.sharpe,
            portfolioHistory: portfolioHistory
        };

        // For simplicity, we are not calculating volatility, sortino, alpha, beta here
        // In a real scenario, you would calculate these.
        portfolio.volatility = 0; 
        portfolio.sortino_ratio = 0;
        portfolio.alpha = 0;
        portfolio.beta = 0;

        renderChart([portfolio], null);
        renderSummaryTable([portfolio], null);

    } catch (error) {
        console.error('Backtest failed:', error);
        displayError(dom.chartContainer, `回測失敗: ${error.message}`);
        renderSummaryTable([], null); // Clear summary table
    } finally {
        dom.runBacktestBtn.disabled = false;
        dom.runBacktestBtn.textContent = '執行回測';
    }
}
