import React from 'react';
import { FaShieldAlt, FaCheckCircle, FaTimesCircle, FaInfoCircle } from 'react-icons/fa';

const Policies: React.FC = () => {
  const policies = [
    {
      id: 1,
      name: 'Data Privacy Policy',
      description: 'Ensures user data is protected and handled according to Canadian privacy laws',
      status: 'active',
      lastUpdated: '2024-01-15'
    },
    {
      id: 2,
      name: 'Access Control Policy',
      description: 'Defines who can access different levels of government data',
      status: 'active',
      lastUpdated: '2024-01-10'
    },
    {
      id: 3,
      name: 'Data Retention Policy',
      description: 'Specifies how long different types of data are retained',
      status: 'draft',
      lastUpdated: '2024-01-05'
    }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <FaCheckCircle className="text-green-500" />;
      case 'draft':
        return <FaInfoCircle className="text-yellow-500" />;
      default:
        return <FaTimesCircle className="text-red-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'draft':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-red-100 text-red-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3 mb-6">
        <FaShieldAlt className="text-3xl text-blue-600" />
        <h1 className="text-3xl font-bold text-gray-900">Policy Management</h1>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Active Policies</h2>
        <div className="space-y-4">
          {policies.map((policy) => (
            <div key={policy.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">{policy.name}</h3>
                  <p className="text-gray-600 mb-3">{policy.description}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>Last updated: {policy.lastUpdated}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(policy.status)}
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(policy.status)}`}>
                    {policy.status}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">Policy Evaluation</h3>
        <p className="text-blue-800 mb-4">
          Use the Open Policy Agent to evaluate policies against your data and requirements.
        </p>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
          Evaluate Policy
        </button>
      </div>
    </div>
  );
};

export default Policies;
