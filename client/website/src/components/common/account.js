import './account.less';
import { getAccount } from '../../slices/tradeSlice';
import { useSelector } from 'react-redux';
import { useEffect, useState } from 'react';
import { Progress } from 'antd';

const Account = ({ settings }) => {

    const account = useSelector(getAccount);

    const [ago, setAgo] = useState(0);

    const renderTime = () => {
        const d = new Date(settings.refreshed)
        return `${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}`
    }
    const updateAgo = () => {
        const ms =  new Date().getTime()-settings.refreshed;
        const min = (ms/1000/60);
        setAgo(min.toFixed(2));
    }

    useEffect(() => {
        const timer = setInterval(() => updateAgo(), 1000);
        return () => {
            clearInterval(timer);
        }
    }, [settings])


    if (!account) return;


    return (
        <div className='account'>
            <div className='account__data'>
                <div className='account__item'>
                    <div>Cash</div>
                    <span>${account.cash.toFixed(2)}</span>
                </div>
                <div className='account__item'>
                    <div>Unrealized</div>
                    <span>{account.unrealized_gains.toFixed(2)}%</span>
                </div>
                <div className='account__item'>
                    <div>Positions</div>
                    <span>{account.positions.length}</span>
                </div>
                {settings && <div className='account__item'>
                    <div>Refreshed</div>
                    <span>
                        {renderTime()}
                    </span>
                </div>}
            </div>
            <div className='account__timer'>
                <Progress percent={ago*100} size="small" showInfo={false} strokeColor={{ from: '#43A047', to: '#D81B60' }} />
            </div>
        </div>
    );
};

export default Account;
