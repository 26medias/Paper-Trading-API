// src/slices/tradeSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import { auth } from '../firebaseConfig';

const API_URL = process.env.REACT_APP_API_ENDPOINT;

const initialState = {
    trade: [],
    steps: null, // To store the steps data
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
export const fetchWatchlist = createAsyncThunk('trade/watchlist', async (ticker, { rejectWithValue }) => {
    try {
        const response = await axios.post(`${API_URL}/trade/watchlist`, {
            project: 'main', // special case, single source for data sync
            action: 'list'
        }, {
            headers: {},
        });
        return response.data;
    } catch (error) {
        return rejectWithValue(error.response ? error.response.data : error.message);
    }
});
export const tickerStatus = createAsyncThunk('trade/status', async (ticker, { rejectWithValue }) => {
    try {
        const response = await axios.get(`${API_URL}/trade/status`, {
            headers: {},
            params: {
                project: getProject(),
                ticker: ticker
            },
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
    /*extraReducers: (builder) => {
        builder
            .addCase(fetchPortfolio.fulfilled, (state, action) => {
                state.portfolio = action.payload;
            })
            .addCase(listtrade.fulfilled, (state, action) => {
                state.trade = action.payload;
            })
            .addCase(deleteFile.fulfilled, (state, action) => {
                state.trade = state.trade.filter((file) => file.id !== action.payload);
            })
            .addCase(fetchtradeteps.fulfilled, (state, action) => {
                state.steps = action.payload;
            });
    },*/
});

// Define the selector
export const getSteps = (state) => state.trade.steps;

export const { clearSteps } = tradeSlice.actions;

export default tradeSlice.reducer;
