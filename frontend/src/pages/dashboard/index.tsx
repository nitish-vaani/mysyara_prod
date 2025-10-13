import React, { useEffect, useState, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Button } from 'primereact/button';
import { Toast } from 'primereact/toast';
import { ScaleLoader } from 'react-spinners';
import { useNavigate } from 'react-router-dom';
import { getDashboardData } from '../../common/api';
import { DashboardResponse, TrendData } from '../../common/types';
import { pagePaths } from '../../common/constants';
import './index.css';

const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const toast = useRef<Toast>(null);
    
    const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [period, setPeriod] = useState<string>('7_days');
    const [error, setError] = useState<string | null>(null);

    const show = (summary: string, severity: 'error' | 'info' | 'success' = 'error') => {
        toast.current?.show({ severity, summary, life: 3000 });
    };

    const fetchDashboardData = async (selectedPeriod: string) => {
        try {
            setLoading(true);
            setError(null);
            
            const user_id = localStorage.getItem("fullName");
            if (!user_id) {
                show("Please login first");
                navigate(pagePaths.signin);
                return;
            }

            const response = await getDashboardData(user_id, selectedPeriod);
            
            if (response.data) {
                setDashboardData(response.data);
            } else {
                setError("No data received from server");
            }
        } catch (error) {
            console.error("Error fetching dashboard data:", error);
            setError("Failed to load dashboard data");
            show("Failed to load dashboard data");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDashboardData(period);
    }, [period]);

    const handlePeriodChange = (newPeriod: string) => {
        setPeriod(newPeriod);
    };

    const formatDuration = (duration: number): string => {
        const minutes = Math.floor(duration / 60);
        const seconds = Math.round(duration % 60);
        return `${minutes}m ${seconds}s`;
    };

    const formatChartData = (trends: TrendData[]): any[] => {
        return trends.map(trend => ({
            ...trend,
            formattedDate: period === '1_day' ? trend.date : new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        }));
    };

    if (loading) {
        return (
            <div className="dashboard">
                <div className="loading-container">
                    <ScaleLoader height={40} width={4} radius={8} margin={6} color="#2196F3" />
                </div>
            </div>
        );
    }

    if (error || !dashboardData) {
        return (
            <div className="dashboard">
                <div className="error-message">
                    {error || "Failed to load dashboard data"}
                </div>
                <div style={{ textAlign: 'center' }}>
                    <Button 
                        label="Retry" 
                        icon="pi pi-refresh" 
                        onClick={() => fetchDashboardData(period)}
                        className="p-button-secondary"
                    />
                </div>
            </div>
        );
    }

    const chartData = formatChartData(dashboardData.call_trends);

    return (
        <div className="dashboard">
            <Toast ref={toast} position="bottom-right" />
            
            <div className="dashboard-header">
                <h1>Dashboard</h1>
                <div className="period-toggle">
                    <Button 
                        label="1 Day" 
                        onClick={() => handlePeriodChange('1_day')}
                        outlined={period !== '1_day'}
                        size="small"
                    />
                    <Button 
                        label="7 Days" 
                        onClick={() => handlePeriodChange('7_days')}
                        outlined={period !== '7_days'}
                        size="small"
                    />
                </div>
            </div>

            {/* Metrics Cards */}
            <div className="metrics-grid">
                <div className="metric-card">
                    <h3>
                        <i className="pi pi-phone"></i>
                        Total Calls
                    </h3>
                    <div className="metric-value">{dashboardData.metrics.total_calls.toLocaleString()}</div>
                    <div className="metric-subtitle">
                        {period === '1_day' ? 'Today' : 'Last 7 days'}
                    </div>
                </div>

                <div className="metric-card duration">
                    <h3>
                        <i className="pi pi-clock"></i>
                        Avg Call Duration
                    </h3>
                    <div className="metric-value">{formatDuration(dashboardData.metrics.avg_call_duration)}</div>
                    <div className="metric-subtitle">Average per call</div>
                </div>

                <div className="metric-card duration">
                    <h3>
                        <i className="pi pi-stopwatch"></i>
                        Total Call Duration
                    </h3>
                    <div className="metric-value">{formatDuration(dashboardData.metrics.total_call_duration)}</div>
                    <div className="metric-subtitle">
                        {period === '1_day' ? 'Today' : 'Last 7 days'}
                    </div>
                </div>
            </div>
            

            {/* Charts Section */}
            <div className="charts-section">
                {/* Calls Trend Chart */}
                <div className="chart-container">
                    <h2>Calls Trend - {period === '1_day' ? 'Hourly' : 'Daily'}</h2>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                <XAxis 
                                    dataKey="formattedDate" 
                                    tick={{ fontSize: 12 }}
                                    stroke="#666"
                                />
                                <YAxis tick={{ fontSize: 12 }} stroke="#666" />
                                <Tooltip 
                                    contentStyle={{ 
                                        backgroundColor: 'white', 
                                        border: '1px solid #ddd',
                                        borderRadius: '8px',
                                        fontSize: '14px'
                                    }}
                                    labelFormatter={(label) => period === '1_day' ? `Time: ${label}` : `Date: ${label}`}
                                />
                                <Legend />
                                <Line 
                                    type="monotone" 
                                    dataKey="calls" 
                                    stroke="#2196F3" 
                                    strokeWidth={3}
                                    dot={{ fill: '#2196F3', strokeWidth: 2, r: 4 }}
                                    activeDot={{ r: 6, stroke: '#2196F3', strokeWidth: 2 }}
                                    name="Calls"
                                />
                                {/* Removed the Line for leads */}
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Call Duration Trend Chart */}
                <div className="chart-container">
                    <h2>Average Call Duration - {period === '1_day' ? 'Hourly' : 'Daily'}</h2>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                <XAxis 
                                    dataKey="formattedDate" 
                                    tick={{ fontSize: 12 }}
                                    stroke="#666"
                                />
                                <YAxis 
                                    tick={{ fontSize: 12 }} 
                                    stroke="#666"
                                    tickFormatter={(value) => `${Math.round(value / 60)}m`}
                                />
                                <Tooltip 
                                    contentStyle={{ 
                                        backgroundColor: 'white', 
                                        border: '1px solid #ddd',
                                        borderRadius: '8px',
                                        fontSize: '14px'
                                    }}
                                    labelFormatter={(label) => period === '1_day' ? `Time: ${label}` : `Date: ${label}`}
                                    formatter={(value: any) => [formatDuration(value), 'Duration']}
                                />
                                <Legend />
                                <Bar 
                                    dataKey="duration" 
                                    fill="#FF9800" 
                                    name="Duration (seconds)"
                                    radius={[4, 4, 0, 0]}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;