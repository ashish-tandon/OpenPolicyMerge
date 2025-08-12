import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Policies from './pages/Policies';
import Representatives from './pages/Representatives';
import Parliament from './pages/Parliament';
import Civic from './pages/Civic';
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/policies" element={<Policies />} />
            <Route path="/representatives" element={<Representatives />} />
            <Route path="/parliament" element={<Parliament />} />
            <Route path="/civic" element={<Civic />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
