// src/pages/Portfolio.js
import React, { useState } from 'react';
import MainLayout from '../components/layouts/MainLayout';

import './HomePage.less';
import Market from '../components/common/market';


const PortfolioPage = () => {

    return (
        <MainLayout>
            <Market />
        </MainLayout>
    );
};

export default PortfolioPage;
