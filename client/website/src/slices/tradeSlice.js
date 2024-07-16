// src/slices/tradeSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_ENDPOINT;

const initialState = {
    trade: [],
    steps: null,
    status: {}, // Changed to an object to store status by ticker
};

const getProject = () => localStorage.getItem('project');

export const fetchPortfolio = createAsyncThunk('trade/positions', async (_, { rejectWithValue }) => {
    try {
        const response = await axios.get(`${API_URL}/trade/positions`, {
            headers: {},
            params: { project: getProject() },
        });
        return response.data;
    } catch (error) {
        return rejectWithValue(error.response ? error.response.data : error.message);
    }
});

export const fetchAccount = createAsyncThunk('trade/stats', async (_, { rejectWithValue }) => {
    try {
        const response = await axios.get(`${API_URL}/trade/stats`, {
            headers: {},
            params: { project: getProject() },
        });
        return response.data;
    } catch (error) {
        return rejectWithValue(error.response ? error.response.data : error.message);
    }
});

export const fetchWatchlist = createAsyncThunk('trade/watchlist', async (_, { rejectWithValue }) => {
    try {
        const response = await axios.post(`${API_URL}/trade/watchlist`, {
            project: 'main', // special case, single source for data sync
            action: 'list'
        }, {
            headers: {},
        });
        return response.data.watchlist;
    } catch (error) {
        return rejectWithValue(error.response ? error.response.data : error.message);
    }
});

export const tickerStatus = createAsyncThunk('data/status', async (ticker, { rejectWithValue }) => {
    try {
        const response = await axios.get(`${API_URL}/data/stats`, {
            headers: {},
            params: {
                project: getProject(),
                symbol: ticker
            },
        });
        return { ticker, data: response.data };
    } catch (error) {
        return rejectWithValue(error.response ? error.response.data : error.message);
    }
});
export const getAllStats = createAsyncThunk('data/status/all', async (symbols, { rejectWithValue }) => {
    try {
        const response = await axios.get(`${API_URL}/data/stats`, {
            headers: {},
            params: {
                project: getProject(),
                symbols: symbols
            },
        });
        return response.data;
    } catch (error) {
        return rejectWithValue(error.response ? error.response.data : error.message);
    }
});

export const doBuy = createAsyncThunk('trade/buy', async ([ticker, qty, price], { rejectWithValue }) => {
    try {
        const response = await axios.post(`${API_URL}/trade/buy`, {
            project: getProject(),
            ticker,
            qty: parseFloat(qty),
            price
        }, {
            headers: {},
        });
        return response.data;
    } catch (error) {
        return rejectWithValue(error.response ? error.response.data : error.message);
    }
});

export const doSell = createAsyncThunk('trade/sell', async ([ticker, qty, price], { rejectWithValue }) => {
    try {
        const response = await axios.post(`${API_URL}/trade/sell`, {
            project: getProject(),
            ticker,
            qty: parseFloat(qty),
            price
        }, {
            headers: {},
        });
        return response.data;
    } catch (error) {
        return rejectWithValue(error.response ? error.response.data : error.message);
    }
});

const tradeSlice = createSlice({
    name: 'trade',
    initialState,
    reducers: {
        clearSteps(state) {
            state.steps = null;
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchPortfolio.fulfilled, (state, action) => {
                state.portfolio = action.payload;
            })
            .addCase(fetchAccount.fulfilled, (state, action) => {
                state.account = action.payload;
            })
            .addCase(fetchWatchlist.fulfilled, (state, action) => {
                state.watchlist = action.payload;
            })
            .addCase(tickerStatus.fulfilled, (state, action) => {
                state.status[action.payload.ticker] = action.payload.data;
            })
            .addCase(getAllStats.fulfilled, (state, action) => {
                for (const symbol in action.payload) {
                    console.log({symbol, value:action.payload[symbol]})
                    state.status[symbol] = action.payload[symbol];
                }
            })
    },
});

// Define the selectors
export const getPortfolio = (state) => state.trade.portfolio;
export const getAccount = (state) => state.trade.account;
export const getWatchlist = (state) => state.trade.watchlist;
export const getSteps = (state) => state.trade.steps;
export const getStatus = (state, ticker) => state.trade.status[ticker];

export const { clearSteps } = tradeSlice.actions;

export default tradeSlice.reducer;
