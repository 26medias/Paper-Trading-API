// src/pages/Portfolio.js
import React, { useState } from 'react';
import { Layout, Button, Row, Col, Typography, Card } from 'antd';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../components/layouts/MainLayout';

import './HomePage.less';
import ProjectSelector from '../components/common/project-selector';
import Portfolio from '../components/common/portfolio';
import Market from '../components/common/market';

const { Title, Paragraph } = Typography;
const { Header, Content, Footer } = Layout;

const PortfolioPage = () => {
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false)


    const refresh = () => {
        setIsLoading(true);
        setTimeout(() => setIsLoading(false), 750);
    }

    return (
        <MainLayout>
            <Content className="home-content">
                <Button onClick={refresh}>Refresh</Button>
                {isLoading && <div>Loading...</div>}
                {!isLoading && (
                    <>
                        <Portfolio />
                        <Market />
                    </>
                )}
                
            </Content>
        </MainLayout>
    );
};

export default PortfolioPage;
