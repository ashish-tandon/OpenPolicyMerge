import React from 'react';
import { FaCity, FaCalendarAlt, FaFileAlt, FaMapMarkerAlt } from 'react-icons/fa';

const Civic: React.FC = () => {
  const meetings = [
    {
      id: 1,
      title: 'City Council Meeting',
      municipality: 'Toronto, ON',
      date: '2024-01-20',
      time: '10:00 AM',
      location: 'City Hall, 100 Queen St W'
    },
    {
      id: 2,
      title: 'Planning Committee Meeting',
      municipality: 'Vancouver, BC',
      date: '2024-01-22',
      time: '2:00 PM',
      location: 'City Hall, 453 W 12th Ave'
    }
  ];

  const documents = [
    {
      id: 1,
      title: 'Municipal Budget 2024',
      municipality: 'Montreal, QC',
      type: 'Budget Document',
      date: '2024-01-15',
      size: '2.3 MB'
    },
    {
      id: 2,
      title: 'Development Permit Guidelines',
      municipality: 'Calgary, AB',
      type: 'Policy Document',
      date: '2024-01-10',
      size: '1.8 MB'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3 mb-6">
        <FaCity className="text-3xl text-orange-600" />
        <h1 className="text-3xl font-bold text-gray-900">Civic Data</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Meetings Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Upcoming Meetings</h2>
          <div className="space-y-4">
            {meetings.map((meeting) => (
              <div key={meeting.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <h3 className="text-lg font-medium text-gray-900 mb-2">{meeting.title}</h3>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <FaMapMarkerAlt className="text-gray-400" />
                    <span>{meeting.municipality}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <FaCalendarAlt className="text-gray-400" />
                    <span>{meeting.date} at {meeting.time}</span>
                  </div>
                  <div className="text-gray-500">
                    {meeting.location}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Documents Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Documents</h2>
          <div className="space-y-4">
            {documents.map((doc) => (
              <div key={doc.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <h3 className="text-lg font-medium text-gray-900 mb-2">{doc.title}</h3>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <FaMapMarkerAlt className="text-gray-400" />
                    <span>{doc.municipality}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <FaFileAlt className="text-gray-400" />
                    <span>{doc.type}</span>
                  </div>
                  <div className="flex items-center justify-between text-gray-500">
                    <span>Date: {doc.date}</span>
                    <span>Size: {doc.size}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-orange-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-orange-900 mb-3">Search Civic Data</h3>
        <p className="text-orange-800 mb-4">
          Search through municipal meetings, documents, and civic information across Canada.
        </p>
        <div className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <input
              type="text"
              placeholder="Search term..."
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            />
            <select className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500">
              <option value="">All Provinces</option>
              <option value="ON">Ontario</option>
              <option value="BC">British Columbia</option>
              <option value="AB">Alberta</option>
              <option value="QC">Quebec</option>
            </select>
            <select className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500">
              <option value="">All Types</option>
              <option value="meeting">Meetings</option>
              <option value="document">Documents</option>
              <option value="policy">Policies</option>
            </select>
          </div>
          <button className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors">
            Search
          </button>
        </div>
      </div>
    </div>
  );
};

export default Civic;
