// src/App.js
import React from 'react';
import { Provider } from 'react-redux';
import { store } from './store';
import AppRouter from './Router';

import TimeAgo from 'javascript-time-ago'
import en from 'javascript-time-ago/locale/en'
TimeAgo.addDefaultLocale(en)

const App = () => (
    <Provider store={store}>
        <AppRouter />
    </Provider>
);

export default App;
