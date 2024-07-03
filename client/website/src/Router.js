// src/Router.js
import React from 'react';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import PortfolioPage from './pages/Portfolio';

const AppRouter = () => (
  <Router>
      <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
      </Routes>
  </Router>
);

export default AppRouter;
