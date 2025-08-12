import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FaHome, FaShieldAlt, FaUsers, FaLandmark, FaCity } from 'react-icons/fa';

const Navbar: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', icon: FaHome },
    { path: '/policies', label: 'Policies', icon: FaShieldAlt },
    { path: '/representatives', label: 'Representatives', icon: FaUsers },
    { path: '/parliament', label: 'Parliament', icon: FaLandmark },
    { path: '/civic', label: 'Civic Data', icon: FaCity },
  ];

  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center space-x-2">
            <FaShieldAlt className="text-blue-600 text-2xl" />
            <span className="text-xl font-bold text-gray-800">OpenPolicy Merge</span>
          </Link>
          
          <div className="hidden md:flex space-x-8">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'text-blue-600 bg-blue-50'
                      : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="text-lg" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>
          
          <div className="md:hidden">
            <button className="text-gray-600 hover:text-blue-600">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
