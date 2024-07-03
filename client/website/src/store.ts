// src/store.ts
import { configureStore } from '@reduxjs/toolkit';
import tradeReducer from './slices/tradeSlice';
import appReducer from './slices/appSlice';

export const store = configureStore({
    reducer: {
        app: appReducer,
        trade: tradeReducer,
    },
});

// Define RootState and AppDispatch types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
