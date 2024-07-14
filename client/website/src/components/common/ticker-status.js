// src/components/common/ProjectSelector.js
import React, { useState, useEffect } from 'react';
import { Form, message, Button, Progress } from 'antd';
import { useNavigate } from 'react-router-dom';

import './ticker-status.less';
import { fetchPortfolio, doBuy, doSell, getStatus } from '../../slices/tradeSlice';
import { useDispatch, useSelector } from 'react-redux';
import { runML } from '../../helpers/ml';
import { CheckCircleTwoTone } from '@ant-design/icons';

import { useRef } from 'react';

const TickerStatus = ({ ticker, isCrypto }) => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const [form] = Form.useForm();

    const [messageApi, contextHolder] = message.useMessage();
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(false)
    const [rnd, setRnd] = useState(0)
    const [displayChart, setDisplayChart] = useState(false)
    const [qty, setQty] = useState(10);
    const [prevInference, setPrevInference] = useState(null);
    const [inference, setInference] = useState(null);
    const [score, setScore] = useState(0);

    const API_URL = process.env.REACT_APP_API_ENDPOINT;

    const status = useSelector(state => getStatus(state, ticker));

    const timeframes = ['1min', '1h', '1d', '5d'];


    const buyRef = useRef(new Audio('/buy.mp3'));
    const sellRef = useRef(new Audio('/sell.mp3'));




    useEffect(() => {
        if (error) {
            messageApi.error(error);
            setError(null); // Reset error after showing the message
        }
    }, [error, messageApi]);


    useEffect(() => {
        if (status) {
            setRnd(Math.random());
            runInference();
        }
    }, [status]);



    const refresh = async () => {
        try {
            await dispatch(fetchPortfolio())
        } catch (e) {}
    }

    

    function colorFromGradient({ value, range, cmap }) {
        const [min, max] = range;
        const numColors = cmap.length;
      
        if (numColors < 2) throw new Error('Color map must have at least two colors.');
      
        // Clamp the value to be within the range
        const clampedValue = Math.max(min, Math.min(value, max));
      
        // Normalize the value to a range of 0 to 1
        const normalizedValue = (clampedValue - min) / (max - min);
      
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
          Math.round(color1[2] + (color2[2] - color1[2]) * t),
        ];
      
        return `rgb(${interpolatedColor[0]}, ${interpolatedColor[1]}, ${interpolatedColor[2]})`;
    }

    const buy = async () => {
        if (!status) return;
        setIsLoading(true);
        const data = status.last_10[status.last_10.length-1];
        try {
            const response = await dispatch(doBuy([ticker, qty, data.Close])).unwrap();
            await refresh();
            setIsLoading(false);
            console.log(response)
        } catch (error) {
            console.log(error.error)
            setError(error.error.toString());
            setIsLoading(false);
        }
    }
    const sell = async () => {
        if (!status) return;
        setIsLoading(true);
        const data = status.last_10[status.last_10.length-1];
        try {
            const response = await dispatch(doSell([ticker, qty, data.Close])).unwrap();
            await refresh();
            setIsLoading(false);
            console.log(response)
        } catch (error) {
            console.log(error.error)
            setError(error.error.toString());
            setIsLoading(false);
        }
    }


    // ML Inference
    const runInference = async () => {
        if (!status) return;
        let columns = ['value', 'value1', 'value2', 'value3', 'delta0', 'delta1', 'delta2'];
        let inferenceData = []
        try {

            setPrevInference(inference);

            timeframes.forEach(timeframe => {
                columns.forEach(column => {
                    const value = status.status[timeframe][column]
                    inferenceData.push(value);
                })
            })
            const prediction = await runML(inferenceData);

            // Calculate the side probability
            let _buy = 0;
            let _sell = 0;
            prediction.forEach((item, n) => {
                if (item.type=="buy") {
                    _buy += item.value.probability;
                    if (item.value.probability > 0.5 && (prevInference && prevInference[n].value.probability <= 0.5)) {
                        try {
                            buyRef.current.play();
                        } catch(e) {
                            console.log(e.message)
                        }
                        
                    }
                } else {
                    _sell += item.value.probability;
                    if (item.value.probability > 0.5 && (prevInference && prevInference[n].value.probability <= 0.5)) {
                        try {
                            sellRef.current.play();
                        } catch(e) {
                            console.log(e.message)
                        }
                    }
                }
            })

            setScore(_buy-_sell)

            //console.log(prediction)
            setInference(prediction);
        } catch (e) {
            setInference(null);
        }
    };


    const cmap_mc = [[49, 206, 83], [38, 92, 153], [235, 51, 51]];
    const cmap_change = [[235, 51, 51], [38, 92, 153], [49, 206, 83]];
    const cmap_score = [[235, 51, 51], [38, 92, 153], [49, 206, 83]];

    const range_mc = [0, 100];
    const range_change = [-10, 10];
    const range_score = [-1, 1];

    const handleChange = (e) => {
        // Get the new value from the input
        const newValue = e.target.value;
    
        // Set the new value to the state
        setQty(newValue);
    
        // Log the new value (for demonstration purposes)
        console.log(newValue);
    };

    const extraClass = isCrypto ? 'ticker-status--crypto' : '';

    const renderBox = () => {
        if (!status) return;
        const data = status.last_10[status.last_10.length-1];

        const change_score = score ? colorFromGradient({
            value: score,
            range: range_score,
            cmap: cmap_score
        }) : 'rgba(0,0,0,0.1)';

        return (
            <div className={`ticker-status ticker-status--status ${extraClass}`}>
                <div className='ticker-status__side' style={{backgroundColor:change_score}}></div>
                <div className='ticker-status__ticker' onClick={() => setDisplayChart(!displayChart)}>
                    {status.ticker}
                </div>
                <div className='ticker-status__price' onClick={() => setDisplayChart(!displayChart)}>
                    ${data.Close.toFixed(4)}
                </div>
                <div className='ticker-status__status' onClick={() => setDisplayChart(!displayChart)}>
                    <div className='ticker-status__status__data'>
                        {timeframes.map((timeframe) => {
                            let value = status.status[timeframe].value ? status.status[timeframe].value.toFixed(2) : '-';
                            let value1 = status.status[timeframe].value1 ? status.status[timeframe].value1.toFixed(2) : '-';
                            let value2 = status.status[timeframe].value2 ? status.status[timeframe].value2.toFixed(2) : '-';

                            const mc_color = status.status[timeframe].value ? colorFromGradient({
                                value: status.status[timeframe].value,
                                range: range_mc,
                                cmap: cmap_mc
                            }) : 'rgba(0,0,0,0.1)';

                            const change_color1 = status.status[timeframe].delta0 ? colorFromGradient({
                                value: status.status[timeframe].delta1,
                                range: range_change,
                                cmap: cmap_change
                            }) : 'rgba(0,0,0,0.1)';

                            const change_color2 = status.status[timeframe].delta1 ? colorFromGradient({
                                value: status.status[timeframe].delta2,
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
                <div className='ticker-status__actions'>
                    <Button size='small' type='primary' onClick={buy}>BUY</Button>
                    <input type='number' value={qty} onChange={handleChange} />
                    <Button size='small' type='primary' danger onClick={sell}>SELL</Button>
                </div>
                <div className='ticker-status__ml'>
                    {inference && inference.map((item) => (
                        <div key={item.name} className={'ticker-status__ml__row ' + (item.value.value ? 'ticker-status__ml__row--signal' : '')}>
                            <div className='ticker-status__ml__row__name'>
                                {item.name}
                            </div>
                            <div className='ticker-status__ml__row__probability'>
                                {item.value.value ? <CheckCircleTwoTone />: 'wait'}
                            </div>
                            <Progress percent={item.value.probability*100} size="small" showInfo={false} strokeColor={{ from: '#D81B60', to: '#43A047' }} />
                        </div>
                    ))}
                </div>
                <div className='ticker-status__date'>
                    {new Date(data.Datetime*1000).toLocaleTimeString()}
                </div>
                
            </div>
        )
    }
    const renderChart = () => {
        if (!status) return;
        const data = status.last_10[status.last_10.length-1];
        return (
            <div className={`ticker-status ticker-status--chart ${extraClass}`}>
                <div className='ticker-status__ticker' onClick={() => setDisplayChart(!displayChart)}>
                    {status.ticker}
                </div>
                <div className='ticker-status__price' onClick={() => setDisplayChart(!displayChart)}>
                    ${data.Close.toFixed(3)}
                </div>
                <div className='ticker-status__chart' onClick={() => setDisplayChart(!displayChart)}>
                    <img src={`${API_URL}/trade/img-candles?ticker=${ticker}&rnd=${rnd}`} />
                </div>
            </div>
        )
    }

    const renderLoading = () => (
        <div className='ticker-status'>
            Loading {ticker}...
        </div>
    )

    return (
        <>
            {contextHolder}
            {(!status || isLoading) && renderLoading()}
            {!isLoading && status && !displayChart && renderBox()}
            {!isLoading && status && displayChart && renderChart()}
        </>
    );
};

export default TickerStatus;
