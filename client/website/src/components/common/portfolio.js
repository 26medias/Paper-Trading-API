// src/components/common/ProjectSelector.js
import React, { useState, useEffect } from 'react';
import { Form, Input, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import { LockFilled } from '@ant-design/icons';

import './portfolio.less';
import { getPortfolio } from '../../slices/tradeSlice';
import { useDispatch, useSelector } from 'react-redux';

const Portfolio = ({ data }) => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const [form] = Form.useForm();

    const positions = useSelector(getPortfolio);

    return (
        <div className='portfolio'>
            <table>
                <thead>
                    <tr>
                        <th>Ticker</th>
                        <th>Qty</th>
                        <th>Avg Cost</th>
                        <th>Latest</th>
                        <th>Profits</th>
                        <th>Gains</th>
                    </tr>
                </thead>
                <tbody>
                    {positions && positions.positions.map((item) => (
                        <tr key={`row-${item.ticker}`}>
                            <td>{item.ticker}</td>
                            <td>{item.qty}</td>
                            <td>${item.avg_cost.toFixed(3)}</td>
                            <td>${item.current_price.toFixed(3)}</td>
                            <td>${item.profit.toFixed(2)}</td>
                            <td>{item.gains.toFixed(2)}%</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Portfolio;
