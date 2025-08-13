import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { RefreshCw, AlertCircle, CheckCircle, XCircle, Clock } from 'lucide-react';

const ServicesDashboard = () => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  const serviceList = [
    { name: 'Policy Service', port: 9001, endpoint: '/healthz', type: 'Python' },
    { name: 'Search Service', port: 9002, endpoint: '/healthz', type: 'Python' },
    { name: 'Auth Service', port: 9003, endpoint: '/healthz', type: 'Python' },
    { name: 'Notification Service', port: 9004, endpoint: '/healthz', type: 'Python' },
    { name: 'Config Service', port: 9005, endpoint: '/healthz', type: 'Python' },
    { name: 'Health Service', port: 9006, endpoint: '/healthz', type: 'Python' },
    { name: 'ETL Service', port: 9007, endpoint: '/healthz', type: 'Python' },
    { name: 'Scraper Service', port: 9008, endpoint: '/healthz', type: 'Python' },
    { name: 'API Gateway', port: 9009, endpoint: '/health', type: 'Go' },
    { name: 'Monitoring Service', port: 9010, endpoint: '/healthz', type: 'Python' },
    { name: 'Plotly Service', port: 9011, endpoint: '/healthz', type: 'Python' },
    { name: 'MCP Service', port: 9012, endpoint: '/healthz', type: 'Python' },
    { name: 'OP-Import Service', port: 9013, endpoint: '/healthz', type: 'Python' },
    { name: 'Web Frontend', port: 3000, endpoint: '/', type: 'Next.js' },
    { name: 'Admin Dashboard', port: 3001, endpoint: '/', type: 'Next.js' },
    { name: 'Mobile API', port: 8081, endpoint: '/', type: 'Expo' },
    { name: 'Legacy Django', port: 8000, endpoint: '/', type: 'Django' }
  ];

  const checkServiceHealth = async (service) => {
    try {
      const response = await fetch(`http://localhost:${service.port}${service.endpoint}`, {
        method: 'GET',
        mode: 'no-cors',
        signal: AbortSignal.timeout(3000)
      });
      return { status: 'healthy', response: 'OK' };
    } catch (error) {
      if (error.name === 'AbortError') {
        return { status: 'timeout', response: 'Timeout' };
      }
      return { status: 'error', response: error.message };
    }
  };

  const checkAllServices = async () => {
    setLoading(true);
    const healthChecks = await Promise.allSettled(
      serviceList.map(service => checkServiceHealth(service))
    );

    const updatedServices = serviceList.map((service, index) => {
      const result = healthChecks[index];
      if (result.status === 'fulfilled') {
        return { ...service, ...result.value };
      } else {
        return { ...service, status: 'error', response: 'Failed to check' };
      }
    });

    setServices(updatedServices);
    setLastUpdated(new Date());
    setLoading(false);
  };

  useEffect(() => {
    checkAllServices();
    const interval = setInterval(checkAllServices, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'timeout':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'healthy':
        return <Badge variant="default" className="bg-green-500">Healthy</Badge>;
      case 'error':
        return <Badge variant="destructive">Error</Badge>;
      case 'timeout':
        return <Badge variant="secondary" className="bg-yellow-500">Timeout</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  const getServiceTypeColor = (type) => {
    switch (type) {
      case 'Python':
        return 'bg-blue-100 text-blue-800';
      case 'Go':
        return 'bg-green-100 text-green-800';
      case 'Next.js':
        return 'bg-purple-100 text-purple-800';
      case 'Expo':
        return 'bg-orange-100 text-orange-800';
      case 'Django':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const healthyCount = services.filter(s => s.status === 'healthy').length;
  const errorCount = services.filter(s => s.status === 'error').length;
  const timeoutCount = services.filter(s => s.status === 'timeout').length;

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">OpenPolicy Services Dashboard</h1>
        <p className="text-gray-600">Real-time monitoring of all microservices</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-sm font-medium text-gray-600">Healthy</p>
                <p className="text-2xl font-bold text-green-600">{healthyCount}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <XCircle className="h-5 w-5 text-red-500" />
              <div>
                <p className="text-sm font-medium text-gray-600">Errors</p>
                <p className="text-2xl font-bold text-red-600">{errorCount}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-yellow-500" />
              <div>
                <p className="text-sm font-medium text-gray-600">Timeouts</p>
                <p className="text-2xl font-bold text-yellow-600">{timeoutCount}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-gray-500" />
              <div>
                <p className="text-sm font-medium text-gray-600">Total</p>
                <p className="text-2xl font-bold text-gray-600">{services.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Controls */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-4">
          <Button onClick={checkAllServices} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh All
          </Button>
          {lastUpdated && (
            <p className="text-sm text-gray-500">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
          )}
        </div>
        <div className="text-sm text-gray-500">
          Auto-refresh every 30 seconds
        </div>
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {services.map((service, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{service.name}</CardTitle>
                {getStatusIcon(service.status)}
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="text-xs">
                  Port {service.port}
                </Badge>
                <Badge className={`text-xs ${getServiceTypeColor(service.type)}`}>
                  {service.type}
                </Badge>
                {getStatusBadge(service.status)}
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-2">
                <div className="text-sm">
                  <span className="font-medium">Endpoint:</span> {service.endpoint}
                </div>
                <div className="text-sm">
                  <span className="font-medium">Status:</span> {service.response}
                </div>
                <div className="text-sm">
                  <span className="font-medium">URL:</span>{' '}
                  <a
                    href={`http://localhost:${service.port}${service.endpoint}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    http://localhost:{service.port}{service.endpoint}
                  </a>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Error Summary */}
      {errorCount > 0 && (
        <Card className="mt-8 border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-red-800">Service Errors Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {services
                .filter(s => s.status === 'error')
                .map((service, index) => (
                  <div key={index} className="flex items-center space-x-2 text-sm">
                    <XCircle className="h-4 w-4 text-red-500" />
                    <span className="font-medium">{service.name}</span>
                    <span className="text-gray-600">(Port {service.port})</span>
                    <span className="text-red-600">- {service.response}</span>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ServicesDashboard;
