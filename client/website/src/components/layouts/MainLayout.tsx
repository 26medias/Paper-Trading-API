import React from 'react';
import { Button } from 'antd';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { AppDispatch } from '../../store';
import './MainLayout.less';
import classNames from 'classnames';

interface MainLayoutProps {
    children: React.ReactNode;
    noPadding?: boolean;
}

const MainLayout = ({ children, noPadding }: MainLayoutProps) => {
    const dispatch = useDispatch<AppDispatch>();
    const navigate = useNavigate();

    const classes = classNames('root', {
        'root--no-padding': noPadding
    });

    return (
        <div className={classes}>
            <header>
                <div onClick={() => navigate('/')} role="button">
                    <img src="https://storage.googleapis.com/irrbb-project/web/logo.png" alt="" />
                    <span>Paper Trading</span>
                </div>
                <div>
                    <Button type="text" icon={<i className="fa-solid fa-house"></i>} onClick={() => navigate('/')}>Dashboard</Button>
                    <Button type="text" icon={<i className="fa-solid fa-chart-simple"></i>} onClick={() => navigate('/portfolio')}>Portfolio</Button>
                </div>
            </header>
            <main>{children}</main>
            <footer>Main Footer</footer>
        </div>
    );
};

export default MainLayout;
