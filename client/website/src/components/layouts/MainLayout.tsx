import React from 'react';
import { useNavigate } from 'react-router-dom';
import './MainLayout.less';
import classNames from 'classnames';

interface MainLayoutProps {
    children: React.ReactNode;
    noPadding?: boolean;
}

const MainLayout = ({ children, noPadding }: MainLayoutProps) => {
    const navigate = useNavigate();

    const classes = classNames('root', {
        'root--no-padding': noPadding
    });
    return (
        <div className={classes}>
            <main>{children}</main>
            <footer>
                <div className='root__nav'>
                    <div onClick={() => navigate('/')}>
                        Project
                    </div>
                    <div onClick={() => navigate('/market')}>
                        Market
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default MainLayout;
