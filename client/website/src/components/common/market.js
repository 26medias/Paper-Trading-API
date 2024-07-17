// src/components/common/Market.js
import React, { useState, useEffect } from 'react';
import { Form, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import TickerStatus from './ticker-status';
import { fetchWatchlist, fetchAccount, getAccount, getWatchlist, tickerStatus, getAllStats, fetchPortfolio, getPortfolio } from '../../slices/tradeSlice';
import { db } from '../../firebaseConfig';
import { doc, onSnapshot } from 'firebase/firestore';
import { w3cwebsocket as W3CWebSocket } from 'websocket';

import './market.less';
import Account from './account';
import Portfolio from './portfolio';
import useMinuteTick from '../../helpers/timer';

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

    const currentMinute = useMinuteTick();

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
        const stockWatchlist = watchlist.filter(ticker => ticker.indexOf('-') === -1).join(',')
        dispatch(getAllStats(stockWatchlist))
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
            refreshPositions();
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
            refreshPositions();
        }
    }, [settings]);

    useEffect(() => {
        const h = new Date().getHours();
        const m = new Date().getMinutes();
        if (h >= 9 && h <= 20) {
            refreshTickers();
            refreshPositions();
        }
    }, [currentMinute]);

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


    const [prices, setPrices] = useState({});
    useEffect(() => {
        if (!watchlist) return;
        const client = new W3CWebSocket(`wss://socket.polygon.io/stocks`);
        const symbols = watchlist.filter(item => item.indexOf('-')==-1);

        client.onopen = () => {
            console.log('WebSocket Client Connected');
            client.send(JSON.stringify({ action: 'auth', params: 'jHDLJmGkm6KtI4H31plpE64mODvl_SMg' }));

            // Subscribe to the symbols
            symbols.forEach(symbol => {
                client.send(JSON.stringify({ action: 'subscribe', params: `T.${symbol}` }));
            });
        };

        client.onmessage = (message) => {
            const data = JSON.parse(message.data);
            data.forEach((msg) => {
                if (msg.ev === 'T') { // Trade event
                    setPrices(prevPrices => ({
                        ...prevPrices,
                        [msg.sym]: msg.p
                    }));
                }
            });
        };

        client.onclose = () => {
            console.log('WebSocket Client Disconnected');
        };

        return () => {
            client.close();
        };
    }, [watchlist]);



    return (
        <div className='market'>
            <div className='market__header'>
                <Account settings={settings} />
            </div>
            <div className='market__content'>
                {watchlist && prices && (
                    <>
                        <div className='market__data'>
                            {false && cryptoWatchlist.map((ticker) => (
                                <TickerStatus ticker={ticker} key={ticker} isCrypto />
                            ))}
                            {stockWatchlist.map((ticker) => (
                                <TickerStatus ticker={ticker} key={ticker} price={prices[ticker]} />
                            ))}
                        </div>
                    </>
                )}

                <Portfolio prices={prices} />

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