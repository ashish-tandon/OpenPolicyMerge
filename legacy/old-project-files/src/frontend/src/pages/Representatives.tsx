import React from 'react';
import { FaUsers, FaMapMarkerAlt, FaEnvelope, FaPhone } from 'react-icons/fa';

const Representatives: React.FC = () => {
  const representatives = [
    {
      id: 1,
      name: 'Justin Trudeau',
      party: 'Liberal Party',
      riding: 'Papineau, Quebec',
      email: 'justin.trudeau@parl.gc.ca',
      phone: '+1-613-992-4211'
    },
    {
      id: 2,
      name: 'Pierre Poilievre',
      party: 'Conservative Party',
      riding: 'Carleton, Ontario',
      email: 'pierre.poilievre@parl.gc.ca',
      phone: '+1-613-992-2772'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3 mb-6">
        <FaUsers className="text-3xl text-green-600" />
        <h1 className="text-3xl font-bold text-gray-900">Canadian Representatives</h1>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Federal Representatives</h2>
        <div className="space-y-4">
          {representatives.map((rep) => (
            <div key={rep.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">{rep.name}</h3>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex items-center space-x-2">
                      <FaMapMarkerAlt className="text-gray-400" />
                      <span>{rep.riding}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="font-medium">Party:</span>
                      <span>{rep.party}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <FaEnvelope className="text-gray-400" />
                      <span>{rep.email}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <FaPhone className="text-gray-400" />
                      <span>{rep.phone}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-green-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-green-900 mb-3">Find Your Representative</h3>
        <p className="text-green-800 mb-4">
          Enter your postal code or coordinates to find your local representatives.
        </p>
        <div className="space-y-3">
          <input
            type="text"
            placeholder="Enter postal code (e.g., K1A 0A6)"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
            Find Representatives
          </button>
        </div>
      </div>
    </div>
  );
};

export default Representatives;
