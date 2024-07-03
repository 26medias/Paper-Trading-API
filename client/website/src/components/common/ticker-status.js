// src/components/common/ProjectSelector.js
import React, { useState, useEffect } from 'react';
import { Form, Input, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import { LockFilled } from '@ant-design/icons';

import './ticker-status.less';
import { tickerStatus } from '../../slices/tradeSlice';
import { useDispatch, useSelector } from 'react-redux';

const TickerStatus = ({ ticker }) => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const [form] = Form.useForm();

    const API_URL = process.env.REACT_APP_API_ENDPOINT;

    const [status, setStatus] = useState();

    const timeframes = ['1m', '1h', '1d', '5d']

    const refresh = async () => {
        const response = await dispatch(tickerStatus(ticker)).unwrap();
        setStatus(response);
    }

    useEffect(() => {
        refresh()
    }, [dispatch]);

    function colorFromGradient({value, range, cmap}) {
        const [min, max] = range;
        const numColors = cmap.length;
      
        if (numColors < 2) throw new Error('Color map must have at least two colors.');
      
        // Normalize the value to a range of 0 to 1
        const normalizedValue = (value - min) / (max - min);
      
        // Calculate the position in the color map
        const scaledValue = normalizedValue * (numColors - 1);
        const colorIndex = Math.floor(scaledValue);
        const t = scaledValue - colorIndex;
      
        // Interpolate between the two nearest colors
        const color1 = cmap[colorIndex];
        const color2 = cmap[colorIndex + 1] || color1; // Handle the edge case
      
        const interpolatedColor = [
            Math.round(color1[0] + (color2[0] - color1[0]) * t),
            Math.round(color1[1] + (color2[1] - color1[1]) * t),
            Math.round(color1[2] + (color2[2] - color1[2]) * t)
        ];
      
        return `rgb(${interpolatedColor[0]}, ${interpolatedColor[1]}, ${interpolatedColor[2]})`;
    }

    const cmap_mc = [[49, 206, 83], [38, 92, 153], [235, 51, 51]];
    const cmap_change = [[49, 206, 83], [38, 92, 153], [235, 51, 51]];

    const range_mc = [0, 100];
    const range_change = [-20, 20];

    const renderBox = () => {
        if (!status) return;
        const data = status.last_10[status.last_10.length-1];
        const data1 = status.last_10[status.last_10.length-2];
        const data2 = status.last_10[status.last_10.length-3];
        return (
            <div className='ticker-status'>
                <div className='ticker-status__ticker'>
                    {status.ticker}
                </div>
                <div className='ticker-status__price'>
                    ${data.Close.toFixed(3)}
                </div>
                <div className='ticker-status__chart'>
                    {/*<img src={`${API_URL}/trade/img-candles?ticker=${ticker}`} />*/}
                </div>
                <div className='ticker-status__status'>
                    <div className='ticker-status__status__data'>
                        {timeframes.map((timeframe) => {
                            let value = data[`marketCycle_${timeframe}`] ? parseFloat(data[`marketCycle_${timeframe}`]).toFixed(2) : '-';
                            let value1 = data1[`marketCycle_${timeframe}`] ? parseFloat(data1[`marketCycle_${timeframe}`]).toFixed(2) : '-';
                            let value2 = data2[`marketCycle_${timeframe}`] ? parseFloat(data2[`marketCycle_${timeframe}`]).toFixed(2) : '-';
                            let change1 = data[`marketCycle_${timeframe}`] && data1[`marketCycle_${timeframe}`] ? (data1[`marketCycle_${timeframe}`]-data[`marketCycle_${timeframe}`]).toFixed(2) : '-';
                            let change2 = data1[`marketCycle_${timeframe}`] && data2[`marketCycle_${timeframe}`] ? (data2[`marketCycle_${timeframe}`]-data1[`marketCycle_${timeframe}`]).toFixed(2) : '-';

                            const mc_color = data[`marketCycle_${timeframe}`] ? colorFromGradient({
                                value: parseFloat(value),
                                range: range_mc,
                                cmap: cmap_mc
                              }) : 'rgba(0,0,0,0.1)';

                              const change_color1 = data[`marketCycle_${timeframe}`] && data1[`marketCycle_${timeframe}`] ? colorFromGradient({
                                  value: parseFloat(change1),
                                  range: range_change,
                                  cmap: cmap_change
                                }) : 'rgba(0,0,0,0.1)';

                                const change_color2 = data1[`marketCycle_${timeframe}`] && data2[`marketCycle_${timeframe}`] ? colorFromGradient({
                                    value: parseFloat(change2),
                                    range: range_change,
                                    cmap: cmap_change
                                  }) : 'rgba(0,0,0,0.1)';

                            return (
                                <div key={`${ticker}-${timeframe}`}>
                                    <div style={{backgroundColor:mc_color}}>{value}</div>
                                    <div style={{backgroundColor:change_color1}}>{value1}</div>
                                    <div style={{backgroundColor:change_color2}}>{value2}</div>
                                    <div>{timeframe}</div>
                                </div>
                            )
                        })}
                    </div>
                </div>
            </div>
        )
    }

    const renderLoading = () => (
        <div className='ticker-status__loading'>
            Loading {ticker}...
        </div>
    )

    return (
        <>
            {!status && renderLoading()}
            {status && renderBox()}
        </>
    );
};

export default TickerStatus;
