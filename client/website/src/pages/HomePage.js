// src/pages/HomePage.js
import React from 'react';
import MainLayout from '../components/layouts/MainLayout';

import './HomePage.less';
import ProjectSelector from '../components/common/project-selector';


const HomePage = () => {

    return (
        <MainLayout>
            <ProjectSelector />
        </MainLayout>
    );
};

export default HomePage;
