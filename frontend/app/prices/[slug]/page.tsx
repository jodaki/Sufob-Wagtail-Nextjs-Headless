"use client";

import { useState, useEffect, useRef } from 'react';
import { useParams } from 'next/navigation';
import { createChart } from 'lightweight-charts';
import { 
    getPricePageBySlug, 
    getPriceChartData,
    getTransactionsFromWagtail 
} from '../../lib/data';

export default function PriceDetailPage() {
    const params = useParams();
    const slug = params?.slug as string;
    
    const [page, setPage] = useState(null);
    const [chartData, setChartData] = useState([]);
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [statistics, setStatistics] = useState({
        latest: 0,
        highest: 0,
        lowest: 0,
        average: 0
    });
    
    const chartContainerRef = useRef(null);
    const chartRef = useRef(null);
    const lineSeriesRef = useRef(null);

    useEffect(() => {
        if (slug) {
            loadPageData();
        }
    }, [slug]);

    useEffect(() => {
        if (chartContainerRef.current && !chartRef.current) {
            initChart();
        }
        
        return () => {
            if (chartRef.current) {
                chartRef.current.remove();
                chartRef.current = null;
            }
        };
    }, []);

    useEffect(() => {
        if (lineSeriesRef.current && chartData.length > 0) {
            lineSeriesRef.current.setData(chartData);
        }
    }, [chartData]);

    const loadPageData = async () => {
        setLoading(true);
        try {
            // Load page from Wagtail
            const pageData = await getPricePageBySlug(slug);
            
            if (!pageData) {
                // Handle 404
                return;
            }
            
            setPage(pageData);
            
            // Load chart data for this commodity
            const chartPoints = await getPriceChartData(pageData.commodity_name, pageData.chart_days || 30);
            setChartData(chartPoints);
            
            // Load detailed transactions
            const transactionData = await getTransactionsFromWagtail(pageData.commodity_name);
            if (transactionData.items && transactionData.items.length > 0) {
                setTransactions(transactionData.items.slice(0, 20));
                
                // Calculate statistics
                const prices = transactionData.items.map(item => 
                    parseFloat(item.final_price) || parseFloat(item.base_price) || 0
                ).filter(price => price > 0);

                if (prices.length > 0) {
                    setStatistics({
                        latest: prices[0],
                        highest: Math.max(...prices),
                        lowest: Math.min(...prices),
                        average: prices.reduce((sum, price) => sum + price, 0) / prices.length
                    });
                }
            }
            
        } catch (error) {
            console.error('Error loading page data:', error);
        } finally {
            setLoading(false);
        }
    };

    const initChart = () => {
        if (!chartContainerRef.current) return;

        const chart = createChart(chartContainerRef.current, {
            width: chartContainerRef.current.clientWidth,
            height: 500,
            layout: {
                backgroundColor: '#ffffff',
                textColor: '#333333',
            },
            grid: {
                vertLines: { color: '#e1e1e1' },
                horzLines: { color: '#e1e1e1' },
            },
            crosshair: {
                mode: 1, // CrosshairMode.Normal
            },
            rightPriceScale: {
                borderColor: '#cccccc',
            },
            timeScale: {
                borderColor: '#cccccc',
                timeVisible: true,
                secondsVisible: false,
            },
        });

        const lineSeries = chart.addLineSeries({
            color: '#2196F3',
            lineWidth: 3,
            priceFormat: {
                type: 'custom',
                formatter: (price) => price.toLocaleString() + ' ریال',
            },
        });

        chartRef.current = chart;
        lineSeriesRef.current = lineSeries;

        // Handle resize
        const handleResize = () => {
            chart.applyOptions({ 
                width: chartContainerRef.current?.clientWidth || 0 
            });
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    };

    if (loading) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="text-center">در حال بارگذاری...</div>
            </div>
        );
    }

    if (!page) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="text-center">صفحه یافت نشد</div>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="mb-6">
                <nav className="text-sm text-gray-600 mb-2">
                    <a href="/prices" className="hover:text-blue-600">قیمت کالاها</a>
                    <span className="mx-2">/</span>
                    <span>{page.title}</span>
                </nav>
                <h1 className="text-3xl font-bold">{page.title}</h1>
                <p className="text-xl text-gray-600 mt-2">{page.commodity_name}</p>
            </div>
            
            {page.chart_description && (
                <div 
                    className="mb-8 bg-blue-50 p-6 rounded-lg"
                    dangerouslySetInnerHTML={{ __html: page.chart_description }}
                />
            )}
            
            <div className="grid gap-6">
                {/* Chart Container */}
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-xl font-semibold">نمودار قیمت {page.commodity_name}</h2>
                        <div className="text-sm text-gray-500">
                            آخرین {page.chart_days || 30} روز
                        </div>
                    </div>
                    <div ref={chartContainerRef} style={{ height: '500px' }} />
                </div>
                
                {/* Statistics */}
                {page.show_statistics && chartData.length > 0 && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="bg-blue-50 p-4 rounded-lg">
                            <h3 className="text-lg font-medium text-blue-800">آخرین قیمت</h3>
                            <p className="text-2xl font-bold text-blue-900">
                                {statistics.latest.toLocaleString()}
                            </p>
                            <span className="text-sm text-blue-600">ریال</span>
                        </div>
                        <div className="bg-green-50 p-4 rounded-lg">
                            <h3 className="text-lg font-medium text-green-800">بالاترین قیمت</h3>
                            <p className="text-2xl font-bold text-green-900">
                                {statistics.highest.toLocaleString()}
                            </p>
                            <span className="text-sm text-green-600">ریال</span>
                        </div>
                        <div className="bg-red-50 p-4 rounded-lg">
                            <h3 className="text-lg font-medium text-red-800">پایین‌ترین قیمت</h3>
                            <p className="text-2xl font-bold text-red-900">
                                {statistics.lowest.toLocaleString()}
                            </p>
                            <span className="text-sm text-red-600">ریال</span>
                        </div>
                        <div className="bg-yellow-50 p-4 rounded-lg">
                            <h3 className="text-lg font-medium text-yellow-800">میانگین قیمت</h3>
                            <p className="text-2xl font-bold text-yellow-900">
                                {Math.round(statistics.average).toLocaleString()}
                            </p>
                            <span className="text-sm text-yellow-600">ریال</span>
                        </div>
                    </div>
                )}
                
                {/* Price Table */}
                <div className="bg-white p-6 rounded-lg shadow">
                    <h2 className="text-xl font-semibold mb-4">تاریخچه معاملات {page.commodity_name}</h2>
                    <div className="overflow-x-auto">
                        <table className="min-w-full table-auto">
                            <thead>
                                <tr className="bg-gray-50">
                                    <th className="px-4 py-2 text-right">تاریخ</th>
                                    <th className="px-4 py-2 text-right">قیمت نهایی</th>
                                    <th className="px-4 py-2 text-right">قیمت پایه</th>
                                    <th className="px-4 py-2 text-right">حجم (تن)</th>
                                    <th className="px-4 py-2 text-right">تولیدکننده</th>
                                    <th className="px-4 py-2 text-right">نوع تسویه</th>
                                </tr>
                            </thead>
                            <tbody>
                                {transactions.length > 0 ? (
                                    transactions.map((transaction, index) => (
                                        <tr key={index} className="hover:bg-gray-50">
                                            <td className="px-4 py-2 border-b">
                                                {transaction.transaction_date}
                                            </td>
                                            <td className="px-4 py-2 border-b font-semibold">
                                                {(transaction.final_price || transaction.base_price || 0).toLocaleString()}
                                            </td>
                                            <td className="px-4 py-2 border-b">
                                                {(transaction.base_price || 0).toLocaleString()}
                                            </td>
                                            <td className="px-4 py-2 border-b">
                                                {(transaction.contract_volume || 0).toLocaleString()}
                                            </td>
                                            <td className="px-4 py-2 border-b text-sm">
                                                {(transaction.producer || '-').substring(0, 20)}
                                            </td>
                                            <td className="px-4 py-2 border-b text-sm">
                                                {transaction.settlement_type || '-'}
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                                            هیچ داده‌ای برای این کالا یافت نشد
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                {/* Additional Info */}
                <div className="bg-gray-50 p-6 rounded-lg">
                    <h3 className="text-lg font-semibold mb-3">اطلاعات تکمیلی</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                            <strong>تعداد کل معاملات:</strong> {transactions.length} مورد
                        </div>
                        <div>
                            <strong>آخرین به‌روزرسانی:</strong> 
                            {transactions.length > 0 ? ` ${transactions[0].transaction_date}` : ' -'}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
