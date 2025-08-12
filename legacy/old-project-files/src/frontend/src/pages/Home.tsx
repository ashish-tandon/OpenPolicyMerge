import React from 'react';
import { Link } from 'react-router-dom';
import { FaShieldAlt, FaUsers, FaLandmark, FaCity, FaDatabase, FaChartLine } from 'react-icons/fa';

const Home: React.FC = () => {
  const features = [
    {
      icon: FaShieldAlt,
      title: 'Policy Management',
      description: 'Comprehensive policy evaluation and management using Open Policy Agent',
      link: '/policies',
      color: 'bg-blue-500'
    },
    {
      icon: FaUsers,
      title: 'Representatives',
      description: 'Find and explore Canadian elected officials and electoral boundaries',
      link: '/representatives',
      color: 'bg-green-500'
    },
    {
      icon: FaLandmark,
      title: 'Parliamentary Data',
      description: 'Access comprehensive Canadian legislative data and voting records',
      link: '/parliament',
      color: 'bg-purple-500'
    },
    {
      icon: FaCity,
      title: 'Civic Information',
      description: 'Municipal government data, meetings, and documents',
      link: '/civic',
      color: 'bg-orange-500'
    },
    {
      icon: FaDatabase,
      title: 'Data Integration',
      description: 'Unified platform combining multiple government data sources',
      link: '/parliament',
      color: 'bg-red-500'
    },
    {
      icon: FaChartLine,
      title: 'Analytics',
      description: 'Data visualization and policy impact analysis tools',
      link: '/policies',
      color: 'bg-indigo-500'
    }
  ];

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to OpenPolicy Merge
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          A unified civic data platform that brings together Canadian legislative data, 
          policy management, and civic information in one comprehensive system.
        </p>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <Link
              key={index}
              to={feature.link}
              className="group block p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-200 transform hover:-translate-y-1"
            >
              <div className={`inline-flex p-3 rounded-lg text-white mb-4 ${feature.color}`}>
                <Icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                {feature.title}
              </h3>
              <p className="text-gray-600">
                {feature.description}
              </p>
            </Link>
          );
        })}
      </div>

      {/* Stats Section */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Platform Statistics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">9</div>
            <div className="text-gray-600">Integrated Repositories</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">6.5GB</div>
            <div className="text-gray-600">Parliamentary Data</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">15+</div>
            <div className="text-gray-600">API Endpoints</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600">12</div>
            <div className="text-gray-600">Microservices</div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-blue-600 rounded-lg shadow-md p-8 text-center text-white">
        <h2 className="text-2xl font-bold mb-4">
          Ready to explore Canadian civic data?
        </h2>
        <p className="text-blue-100 mb-6">
          Start exploring policies, representatives, and legislative data today.
        </p>
        <div className="space-x-4">
          <Link
            to="/policies"
            className="inline-block bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            Explore Policies
          </Link>
          <Link
            to="/representatives"
            className="inline-block bg-transparent border-2 border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
          >
            Find Representatives
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;
