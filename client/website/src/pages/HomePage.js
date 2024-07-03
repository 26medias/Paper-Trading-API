// src/pages/HomePage.js
import React from 'react';
import { Layout, Button, Row, Col, Typography, Card } from 'antd';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../components/layouts/MainLayout';

import './HomePage.less';
import ProjectSelector from '../components/common/project-selector';

const { Title, Paragraph } = Typography;
const { Header, Content, Footer } = Layout;

const HomePage = () => {
    const navigate = useNavigate();

    const handleSignIn = () => {
        navigate('/auth/signin');
    };

    const handleSignUp = () => {
        navigate('/auth/signup');
    };

    const handleDashboard = () => {
        navigate('/dashboard');
    };

    return (
        <MainLayout>
            <Content className="home-content">
                <div className="home-hero">
                    <Title level={1}>Paper Trading</Title>
                    <Paragraph>
                        Live Market Cycle Paper Trading
                    </Paragraph>
                    <div className="home-buttons">
                        <Button type="default" size="large" className="home-button" onClick={handleDashboard}>Dashboard</Button>
                    </div>

                    <ProjectSelector />
                </div>
            </Content>
        </MainLayout>
    );
};

export default HomePage;
