// src/components/common/ProjectSelector.js
import React, { useState, useEffect } from 'react';
import { Form, Input, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import { LockFilled } from '@ant-design/icons';

import './market.less';
import { fetchWatchlist } from '../../slices/tradeSlice';
import { useDispatch, useSelector } from 'react-redux';
import TickerStatus from './ticker-status';

const Market = ({ data }) => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const [form] = Form.useForm();

    const [isLoading, setIsLoading] = useState(false)
    const [watchlist, setWatchlist] = useState([])
    //const portfolio = useSelector(fetchPortfolio);

    const refresh = async () => {
        setIsLoading(true);
        const response = await dispatch(fetchWatchlist()).unwrap();
        setWatchlist(response.watchlist);
        setIsLoading(false);
    }

    useEffect(() => {
        refresh()
    }, [dispatch]);



    return (
        <div className='market'>
            <div className='market__options'>
                <Button onClick={refresh}>Refresh</Button>
            </div>
            <div className='market__data'>
                {isLoading && <div>Loading...</div>}
                {!isLoading && watchlist.map((ticker) => (
                    <TickerStatus ticker={ticker} key={ticker} />
                ))}
            </div>
            
        </div>
    );
};

export default Market;
