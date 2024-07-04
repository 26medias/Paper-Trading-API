// src/components/common/Market.js
import React, { useState, useEffect } from 'react';
import { Form, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import TickerStatus from './ticker-status';
import { fetchWatchlist, fetchAccount, getAccount, getWatchlist, tickerStatus, fetchPortfolio, getPortfolio } from '../../slices/tradeSlice';
import { db } from '../../firebaseConfig';
import { doc, onSnapshot } from 'firebase/firestore';

import './market.less';
import Account from './account';
import Portfolio from './portfolio';

const Market = ({ data }) => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const [form] = Form.useForm();

    const [messageApi, contextHolder] = message.useMessage();
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [settings, setSettings] = useState(null);

    const account = useSelector(getAccount);
    const portfolio = useSelector(getPortfolio);
    const watchlist = useSelector(getWatchlist);

    const [cryptoWatchlist, setCryptoWatchlist] = useState([]);
    const [stockWatchlist, setStockWatchlist] = useState([]);

    const refresh = async () => {
        setIsLoading(true);
        try {
            await dispatch(fetchWatchlist()).unwrap();
            setIsLoading(false);
        } catch (error) {
            console.log(error.error)
            setError(error.error.toString());
            setIsLoading(false);
        }
    }

    const refreshTickers = async () => {
        if (!watchlist) return;
        watchlist.forEach(ticker => {
            try {
                dispatch(tickerStatus(ticker)).unwrap()
            } catch (error) {
                console.log(error.error)
                setError(error.error.toString());
            }
        });
    }
    const refreshPositions = async () => {
        try {
            await dispatch(fetchPortfolio())
        } catch (error) {
            console.log(error.error)
            setError(error.error.toString());
        }
    }
    const refreshAccount = async () => {
        try {
            await dispatch(fetchAccount())
        } catch (error) {
            console.log(error.error)
            setError(error.error.toString());
        }
    }

    useEffect(() => {
        refresh();
        refreshPositions();
    }, []);

    useEffect(() => {
        if (watchlist) {
            refreshTickers();
            setCryptoWatchlist(watchlist.filter(item => item.indexOf('-')!==-1))
            setStockWatchlist(watchlist.filter(item => item.indexOf('-')==-1))
        }
    }, [watchlist]);

    useEffect(() => {
        refreshAccount();
    }, [portfolio]);


    useEffect(() => {
        if (settings) {
            refreshTickers();
        }
    }, [settings]);

    useEffect(() => {
        if (error) {
            messageApi.error(error);
            setError(null); // Reset error after showing the message
        }
    }, [error, messageApi]);


    useEffect(() => {
        const settingsRef = doc(db, 'paper_settings', 'settings');
        const unsubscribe = onSnapshot(settingsRef, (docSnapshot) => {
            if (docSnapshot.exists()) {
                const data = docSnapshot.data();
                console.log("settings", {data});
                setSettings(data);
            } else {
                console.log("No such document!");
            }
        }, (error) => {
            console.log("Error getting document:", error);
        });

        return () => unsubscribe();
    }, []);

    return (
        <div className='market'>
            <div className='market__header'>
                <Account settings={settings} />
            </div>
            <div className='market__content'>
                {watchlist && (
                    <>
                        <div className='market__data'>
                            {cryptoWatchlist.map((ticker) => (
                                <TickerStatus ticker={ticker} key={ticker} isCrypto />
                            ))}
                            {stockWatchlist.map((ticker) => (
                                <TickerStatus ticker={ticker} key={ticker} />
                            ))}
                        </div>
                    </>
                )}

                <Portfolio />

                {settings && (
                    <div className='market__settings'>
                        <p>Refreshed {new Date(settings.refreshed).toTimeString()}</p>
                    </div>
                )}

                {(isLoading || !watchlist || !account || !portfolio) && <div className='market__loading'>Loading...</div>}
            </div>
        </div>
    );
};

export default Market;