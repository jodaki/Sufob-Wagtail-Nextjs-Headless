"use client";

import { useState, useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';
import { 
    getPricePages, 
    getPriceIndexPages, 
    getTransactionsFromWagtail, 
    getCommoditiesFromWagtail,
    getPriceChartData 
} from '../lib/data';

export default function PricesPage() {
    const [pricePages, setPricePages] = useState<any[]>([]);
    const [indexPage, setIndexPage] = useState<any>(null);
    const [selectedCommodity, setSelectedCommodity] = useState<string>('');
    const [commodities, setCommodities] = useState<any[]>([]);
    const [chartData, setChartData] = useState<any[]>([]);
    const [transactions, setTransactions] = useState<any[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [statistics, setStatistics] = useState({
        latest: 0,
        highest: 0,
        lowest: 0,
        average: 0
    });
    
    const chartContainerRef = useRef<HTMLDivElement | null>(null);
    const chartRef = useRef<any>(null);
    const lineSeriesRef = useRef<any>(null);

    // Load data on component mount
    useEffect(() => {
        loadInitialData();
    }, []);

    // Initialize chart when container is ready
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

    // Update chart when data changes
    useEffect(() => {
        if (lineSeriesRef.current && chartData.length > 0) {
            lineSeriesRef.current.setData(chartData);
        }
    }, [chartData]);

    const loadInitialData = async () => {
        try {
            // Load index page
            const indexData = await getPriceIndexPages();
            if (indexData.items && indexData.items.length > 0) {
                setIndexPage(indexData.items[0]);
            }

            // Load price pages (created in Wagtail admin)
            const pagesData = await getPricePages();
            setPricePages(pagesData.items || []);

            // Load commodities
            const commoditiesData = await getCommoditiesFromWagtail();
            setCommodities(commoditiesData);
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    };

    const initChart = () => {
        if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current as HTMLDivElement, {
        width: (chartContainerRef.current as HTMLDivElement).clientWidth,
            height: 400,
            layout: {
                background: '#ffffff' as any,
                textColor: '#333333' as any,
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

    const lineSeries = (chart as any).addLineSeries({
            color: '#2196F3',
            lineWidth: 2,
            priceFormat: {
                type: 'custom',
        formatter: (price: number) => price.toLocaleString() + ' ریال',
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

    const loadPriceData = async () => {
        if (!selectedCommodity) {
            alert('لطفاً یک کالا انتخاب کنید');
            return;
        }

        setLoading(true);
        try {
            // Get chart data
            // New: use TradingView-friendly API (fallback: transactions if needed)
            const chartPoints = await getPriceChartData(selectedCommodity, 30);
            setChartData(chartPoints);

            // Get detailed transactions
            const data = await getTransactionsFromWagtail(selectedCommodity as any);
            if (data.items && data.items.length > 0) {
                setTransactions(data.items.slice(0, 20));
                
                // Calculate statistics
                const prices = data.items.map((item: any) => 
                    parseFloat(item.final_price) || parseFloat(item.base_price) || 0
                ).filter((price: number) => price > 0);

                if (prices.length > 0) {
                    setStatistics({
                        latest: prices[0] as number,
                        highest: Math.max(...prices),
                        lowest: Math.min(...prices),
                        average: prices.reduce((sum: number, price: number) => sum + price, 0) / prices.length
                    });
                }
            }
        } catch (error) {
            console.error('Error loading price data:', error);
            alert('خطا در بارگذاری داده‌ها');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-6">
                {indexPage ? indexPage.title : 'قیمت کالاها'}
            </h1>
            
            {/* Index page intro */}
            {indexPage && indexPage.intro && (
                <div className="bg-gray-50 p-6 rounded-lg mb-6" 
                     dangerouslySetInnerHTML={{ __html: indexPage.intro }} />
            )}

            {/* Price Pages from Wagtail */}
            {pricePages.length > 0 && (
                <div className="mb-8">
                    <h2 className="text-2xl font-semibold mb-4">صفحات قیمت</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {pricePages.map((page) => (
                            <div key={page.id} className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
                                <h3 className="text-xl font-semibold mb-2">
                                    <a href={`/prices/${page.slug}/`} className="text-blue-600 hover:text-blue-800">
                                        {page.title}
                                    </a>
                                </h3>
                                <p className="text-gray-600 mb-4">
                                    {page.get_main_category_name || ''}
                                    {page.get_category_name ? ` / ${page.get_category_name}` : ''}
                                    {page.get_subcategory_name ? ` / ${page.get_subcategory_name}` : ''}
                                </p>
                                {page.chart_description && (
                                    <div 
                                        className="text-sm text-gray-500"
                                        dangerouslySetInnerHTML={{ __html: page.chart_description }}
                                    />
                                )}
                                <div className="mt-4">
                                    <a 
                                        href={`/prices/${page.slug}/`} 
                                        className="inline-block bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
                                    >
                                        مشاهده چارت
                                    </a>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
            
            {/* Quick Chart Section */}
            <div className="grid gap-6">
                {/* Commodity Selection */}
                <div className="bg-white p-6 rounded-lg shadow">
                    <h2 className="text-xl font-semibold mb-4">نمایش سریع چارت</h2>
                    <div className="flex gap-4 items-center">
                        <select
                            value={selectedCommodity}
                            onChange={(e) => setSelectedCommodity(e.target.value)}
                            className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                            <option value="">انتخاب کالا...</option>
                            {commodities.map((commodity, index) => (
                                <option key={index} value={commodity.name}>
                                    {commodity.name}
                                </option>
                            ))}
                        </select>
                        <button
                            onClick={loadPriceData}
                            disabled={loading || !selectedCommodity}
                            className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'در حال بارگذاری...' : 'نمایش چارت'}
                        </button>
                    </div>
                </div>

                {/* Chart Container */}
                {chartData.length > 0 && (
                    <div className="bg-white p-6 rounded-lg shadow">
                        <h2 className="text-xl font-semibold mb-4">
                            نمودار قیمت {selectedCommodity}
                        </h2>
                        <div ref={chartContainerRef} style={{ height: '400px' }} />
                    </div>
                )}

                {/* Statistics */}
                {chartData.length > 0 && (
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
                {transactions.length > 0 && (
                    <div className="bg-white p-6 rounded-lg shadow">
                        <h2 className="text-xl font-semibold mb-4">
                            آخرین معاملات {selectedCommodity}
                        </h2>
                        <div className="overflow-x-auto">
                            <table className="min-w-full table-auto">
                                <thead>
                                    <tr className="bg-gray-50">
                                        <th className="px-4 py-2 text-right">تاریخ</th>
                                        <th className="px-4 py-2 text-right">قیمت نهایی</th>
                                        <th className="px-4 py-2 text-right">حجم (تن)</th>
                                        <th className="px-4 py-2 text-right">تولیدکننده</th>
                                        <th className="px-4 py-2 text-right">نوع تسویه</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {transactions.map((transaction, index) => (
                                        <tr key={index} className="hover:bg-gray-50">
                                            <td className="px-4 py-2 border-b">
                                                {transaction.transaction_date}
                                            </td>
                                            <td className="px-4 py-2 border-b font-semibold">
                                                {(transaction.final_price || transaction.base_price || 0).toLocaleString()}
                                            </td>
                                            <td className="px-4 py-2 border-b">
                                                {(transaction.contract_volume || 0).toLocaleString()}
                                            </td>
                                            <td className="px-4 py-2 border-b text-sm">
                                                {transaction.producer || '-'}
                                            </td>
                                            <td className="px-4 py-2 border-b text-sm">
                                                {transaction.settlement_type || '-'}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
