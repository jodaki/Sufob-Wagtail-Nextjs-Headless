"use client";

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { 
    getPricePageBySlug, 
    getPriceSeries,
    getTransactionsFromWagtail 
} from '../../lib/data';
import { 
    PriceChart, 
    PriceSummary, 
    TransactionsTable, 
    BlogPosts 
} from '../../components/features/price-page';

export default function PriceDetailPage() {
    const params = useParams();
    const slug = params?.slug as string;
    
    const [page, setPage] = useState<any>(null);
    const [chartData, setChartData] = useState<any>({});
    const [transactions, setTransactions] = useState<any[]>([]);
    const [latestPosts, setLatestPosts] = useState<any[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [priceData, setPriceData] = useState<any>(null);
    const [transactionData, setTransactionData] = useState<any>(null);

    useEffect(() => {
        if (slug) {
            setErrorMessage(null);
            loadPageData();
        } else {
            setLoading(false);
            setErrorMessage('صفحه یافت نشد');
        }
        // eslint-disable-next-line
    }, [slug]);

    // تعریف متغیرهای chartPeriods و chartDataMap درون تابع loadPageData
    const loadPageData = async () => {
        setLoading(true);
        try {
            const pageData: any = await getPricePageBySlug(slug);
            if (!pageData) {
                setPage(null);
                setErrorMessage('صفحه یافت نشد');
                return;
            }
            setPage(pageData);
            // Load chart data for multiple periods
            const chartPeriods = ['1D', '1W', '1M', '1Y'];
            const periodMapping = {
                '1D': 'daily',
                '1W': 'weekly', 
                '1M': 'monthly',
                '1Y': 'yearly'
            };
            
            let chartDataMap: any = {};
            for (const period of chartPeriods) {
                try {
                    const mappedPeriod = periodMapping[period as keyof typeof periodMapping];
                    const response = await getPriceSeries(pageData.slug, mappedPeriod, pageData.chart_days || 30);
                    
                    console.log(`API Response for ${period}:`, response);
                    
                    let seriesData = [];
                    if (Array.isArray(response)) {
                        seriesData = response;
                    } else if (response && response.series) {
                        seriesData = response.series;
                    } else if (response && response.periods && response.periods[period]) {
                        seriesData = response.periods[period];
                    }
                    
                    console.log(`Series data for ${period}:`, seriesData);
                    
                    const formattedData = seriesData.map((item: any) => {
                        // داده‌ها از API به صورت { time: '2024-08-09', value: 150000 } می‌آیند
                        return {
                            time: item.time, // تاریخ به فرمت درست است
                            value: parseFloat(item.value) || 0
                        };
                    }).filter((item: any) => item.value > 0);
                    
                    console.log(`Formatted data for ${period}:`, formattedData);
                    chartDataMap[period] = formattedData;
                } catch (error) {
                    console.error(`Error loading ${period} data:`, error);
                    chartDataMap[period] = [];
                }
            }
            console.log('Final chart data map:', chartDataMap);
            setChartData(chartDataMap);
            // Load detailed transactions
            const selectionLabel = pageData.get_subcategory_name || pageData.get_category_name || '';
            const transactionData = await getTransactionsFromWagtail(selectionLabel as any);
            if (transactionData.items && transactionData.items.length > 0) {
                setTransactions(transactionData.items.slice(0, 20));
                // Calculate price summary data
                const prices = transactionData.items.map((item: any) => 
                    parseFloat(item.final_price) || parseFloat(item.base_price) || 0
                ).filter((price: number) => price > 0);
                if (prices.length > 0) {
                    const latest = prices[0];
                    const highest = Math.max(...prices);
                    const lowest = Math.min(...prices);
                    const average = prices.reduce((sum: number, price: number) => sum + price, 0) / prices.length;
                    setPriceData({
                        finalPriceAvg: Math.round(average).toLocaleString(),
                        finalPrice: latest.toLocaleString(),
                        lowestPrice: lowest.toLocaleString(),
                        highestPrice: highest.toLocaleString(),
                        weeklyRange: `${Math.min(...prices.slice(0, 7)).toLocaleString()}-${Math.max(...prices.slice(0, 7)).toLocaleString()}`,
                        monthlyRange: `${Math.min(...prices.slice(0, 30)).toLocaleString()}-${Math.max(...prices.slice(0, 30)).toLocaleString()}`,
                        monthlyChange: '۱۰.۳۵ %+',
                    });
                    const latestTransaction = transactionData.items[0];
                    setTransactionData({
                        settlementType: latestTransaction.settlement_type || 'نقدی',
                        transactionDate: latestTransaction.transaction_date || '1404/04/30',
                        contractVolume: (latestTransaction.contract_volume || 0).toLocaleString(),
                        demand: (latestTransaction.contract_volume || 0).toLocaleString(),
                        supplyVolume: (latestTransaction.contract_volume || 0).toLocaleString(),
                        basePrice: (latestTransaction.base_price || 0).toLocaleString(),
                        transactionValue: (latestTransaction.final_price * latestTransaction.contract_volume || 0).toLocaleString(),
                    });
                }
            }
            if (pageData.get_latest_posts) {
                setLatestPosts(pageData.get_latest_posts);
            }
        } catch (error) {
            setErrorMessage('خطا در بارگذاری داده‌ها');
        } finally {
            setLoading(false);
        }
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
                <div className="text-center text-red-600">{errorMessage || 'صفحه یافت نشد'}</div>
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
                <p className="text-xl text-gray-600 mt-2">
                    {page.get_main_category_name || ''}
                    {page.get_category_name ? ` / ${page.get_category_name}` : ''}
                    {page.get_subcategory_name ? ` / ${page.get_subcategory_name}` : ''}
                </p>
            </div>
            {page.chart_description && (
                <div 
                    className="mb-8 bg-blue-50 p-6 rounded-lg"
                    dangerouslySetInnerHTML={{ __html: page.chart_description }}
                />
            )}
            <div className="space-y-8">
                <div className="bg-white p-6 rounded-lg ">
                    <PriceChart 
                        data={chartData}
                        title={`نمودار قیمت ${page.title}`}
                        height={500}
                        showPeriodButtons={true}
                    />
                </div>
                <div className="bg-white p-6 rounded-lg ">
                    <h2 className="text-xl font-semibold mb-4">خلاصه قیمت و معاملات</h2>
                    <PriceSummary 
                        priceData={priceData}
                        transactionData={transactionData}
                    />
                </div>
                <div className="bg-white p-6 rounded-lg ">
                    <h2 className="text-xl font-semibold mb-4">تاریخچه معاملات {page.get_subcategory_name || page.get_category_name || ''}</h2>
                    <TransactionsTable 
                        transactionsList={Array.isArray(transactions) && transactions.length > 0
                            ? undefined
                            : null}
                        itemsPerPage={10}
                    />
                </div>
                <div className="bg-white p-6 rounded-lg ">
                    <BlogPosts posts={undefined} showCount={3} />
                </div>
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
