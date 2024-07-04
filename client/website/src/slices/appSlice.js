// src/slices/appSlice.js
import { createSlice } from '@reduxjs/toolkit';

const appSlice = createSlice({
    name: 'app',
    initialState: {
        settings: {},
    },
    reducers: {
        setSettings: (state, action) => {
            state.settings = action.payload;
        },
    },
});

export const getSettings = (state) => state.app.settings;
export const { setSettings } = appSlice.actions;
export default appSlice.reducer;
