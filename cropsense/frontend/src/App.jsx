import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Home from './pages/Home';
import DiseaseDetection from './pages/DiseaseDetection';
import YieldPrediction from './pages/YieldPrediction';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <Router>
      <Toaster position="top-right" />
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/detect" element={<DiseaseDetection />} />
          <Route path="/yield" element={<YieldPrediction />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="*" element={
            <div className="h-[60vh] flex flex-col items-center justify-center space-y-4">
              <h1 className="text-6xl font-black text-primary">404</h1>
              <p className="text-on-surface-variant">Page not found</p>
            </div>
          } />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
