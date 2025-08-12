import React from 'react';
import { FaLandmark, FaVoteYea, FaCalendarAlt } from 'react-icons/fa';

const Parliament: React.FC = () => {
  const bills = [
    {
      id: 1,
      title: 'Bill C-18: Online News Act',
      status: 'Royal Assent',
      introduced: '2022-12-05',
      description: 'An Act respecting online communications platforms that make news content available to persons in Canada'
    },
    {
      id: 2,
      title: 'Bill C-11: Online Streaming Act',
      status: 'Royal Assent',
      introduced: '2022-02-02',
      description: 'An Act to amend the Broadcasting Act and to make related and consequential amendments to other Acts'
    }
  ];

  const votes = [
    {
      id: 1,
      bill: 'Bill C-18',
      date: '2023-06-22',
      result: 'Passed',
      yeas: 172,
      nays: 149
    },
    {
      id: 2,
      bill: 'Bill C-11',
      date: '2023-05-18',
      result: 'Passed',
      yeas: 208,
      nays: 113
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3 mb-6">
        <FaLandmark className="text-3xl text-purple-600" />
        <h1 className="text-3xl font-bold text-gray-900">Parliamentary Data</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bills Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Bills</h2>
          <div className="space-y-4">
            {bills.map((bill) => (
              <div key={bill.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <h3 className="text-lg font-medium text-gray-900 mb-2">{bill.title}</h3>
                <p className="text-gray-600 mb-3 text-sm">{bill.description}</p>
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>Introduced: {bill.introduced}</span>
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                    {bill.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Votes Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Votes</h2>
          <div className="space-y-4">
            {votes.map((vote) => (
              <div key={vote.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <h3 className="text-lg font-medium text-gray-900 mb-2">{vote.bill}</h3>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <FaCalendarAlt className="text-gray-400" />
                    <span>Date: {vote.date}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <FaVoteYea className="text-gray-400" />
                    <span>Result: {vote.result}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-green-600">Yeas: {vote.yeas}</span>
                    <span className="text-red-600">Nays: {vote.nays}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-purple-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-purple-900 mb-3">Search Parliamentary Data</h3>
        <p className="text-purple-800 mb-4">
          Search through bills, votes, debates, and other parliamentary proceedings.
        </p>
        <div className="space-y-3">
          <input
            type="text"
            placeholder="Search bills, votes, or debates..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors">
            Search
          </button>
        </div>
      </div>
    </div>
  );
};

export default Parliament;
