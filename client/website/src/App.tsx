// src/App.js
import React from 'react';
import { Provider } from 'react-redux';
import { store } from './store';
import AppRouter from './Router';

const App = () => (
    <Provider store={store}>
        <AppRouter />
    </Provider>
);

export default App;
