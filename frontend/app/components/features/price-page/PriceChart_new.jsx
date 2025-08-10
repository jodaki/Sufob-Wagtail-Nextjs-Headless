"use client";

import React, { useEffect, useRef, useState, useCallback, useMemo } from "react";
import { Box, Card, CardHeader, CardContent, Typography } from "@mui/material";

const PriceChart = ({ data = null, height = 350, title, showPeriodButtons = true }) => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);
  const [activePeriod, setActivePeriod] = useState("1D");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const periodColors = {
    "1D": "#00D2FF",
    "1W": "#FFAB00", 
    "1M": "#FF6B6B",
    "1Y": "#51CF66",
  };

  // داده پیش‌فرض
  const defaultData = {
    "1D": [
      { time: "2025-01-01", value: 54540 },
      { time: "2025-01-02", value: 53920 },
      { time: "2025-01-03", value: 34200 },
      { time: "2025-01-03", value: 54200 },
      { time: "2025-01-03", value: 44200 },
      { time: "2025-01-03", value: 54200 },
      { time: "2025-01-03", value: 54200 },
      { time: "2025-01-03", value: 54200 },
      { time: "2025-01-03", value: 44200 },
      { time: "2025-01-03", value: 34200 },
      { time: "2025-01-03", value: 24200 },
      { time: "2025-01-03", value: 14200 },

      { time: "2025-01-03", value: 54200 },
      { time: "2025-01-03", value: 54200 },
    ],
    "1W": [
      { time: "2025-01-01", value: 54540 },
      { time: "2025-01-08", value: 53920 },
    ],
    "1M": [
      { time: "2025-01-01", value: 54540 },
      { time: "2025-02-01", value: 53920 },
    ],
    "1Y": [
      { time: "2024-01-01", value: 45000 },
      { time: "2025-01-01", value: 48000 },
    ],
  };

  // داده‌ها را پردازش کن
  const processedChartData = useMemo(() => {
    console.log('Raw data received:', data);
    
    if (!data || typeof data !== 'object') {
      console.warn('Invalid raw data, using default data');
      return defaultData;
    }

    const processed = {};
    
    // بررسی کلیدهای موجود و پردازش
    Object.keys(data).forEach(key => {
      const rawArray = data[key];
      console.log(`Processing ${key}:`, rawArray);
      
      if (Array.isArray(rawArray) && rawArray.length > 0) {
        // تبدیل داده‌ها به فرمت مناسب lightweight-charts
        processed[key] = rawArray.map(item => {
          if (item && typeof item === 'object') {
            // ممکن است کلیدها متفاوت باشند
            const time = item.time || item.date || item.timestamp || item.created_at;
            const value = item.value || item.price || item.close || item.amount;
            
            if (time && value !== undefined) {
              return {
                time: time.split('T')[0], // فقط تاریخ، نه زمان
                value: parseFloat(value)
              };
            }
          }
          return null;
        }).filter(item => item !== null);
      } else {
        // اگر داده‌ای نبود از پیش‌فرض استفاده کن
        processed[key] = defaultData[key] || [];
      }
      
      console.log(`${key} processed:`, processed[key]?.length || 0, 'points');
    });

    // اگر هیچ داده‌ای پردازش نشد، از پیش‌فرض استفاده کن
    if (Object.keys(processed).length === 0) {
      console.log('No data processed, using default data');
      return defaultData;
    }

    console.log('Final processed data:', processed);
    return processed;
  }, [data]);

  // تابع تغییر دوره
  const changePeriod = useCallback((period) => {
    if (!seriesRef.current || !chartRef.current || !processedChartData[period]) return;
    
    try {
      seriesRef.current.setData(processedChartData[period]);
      seriesRef.current.applyOptions({ color: periodColors[period] });
      chartRef.current.timeScale().fitContent();
      setActivePeriod(period);
      console.log(`Period changed to ${period}, data points:`, processedChartData[period].length);
    } catch (error) {
      console.error('Error changing period:', error);
    }
  }, [processedChartData, periodColors]);

  // ایجاد چارت فقط یکبار
  useEffect(() => {
    if (!chartContainerRef.current) return;

    // پاک‌سازی کامل container
    chartContainerRef.current.innerHTML = '';

    let isMounted = true;

    const createChart = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Try different ways to import lightweight-charts
        let createChartFn;
        
        try {
          // Method 1: Named import
          const { createChart } = await import("lightweight-charts");
          createChartFn = createChart;
          console.log('Import method 1 successful');
        } catch (e1) {
          console.log('Method 1 failed, trying method 2');
          try {
            // Method 2: Default import
            const LightweightCharts = await import("lightweight-charts");
            createChartFn = LightweightCharts.default?.createChart || LightweightCharts.createChart;
            console.log('Import method 2 successful');
          } catch (e2) {
            console.log('Method 2 failed, trying method 3');
            // Method 3: Full import
            const LightweightCharts = await import("lightweight-charts");
            console.log('LightweightCharts object:', LightweightCharts);
            console.log('Available properties:', Object.keys(LightweightCharts));
            createChartFn = LightweightCharts.createChart;
            console.log('Import method 3 result:', typeof createChartFn);
          }
        }
        
        console.log('createChart function:', typeof createChartFn);

        if (!isMounted || !chartContainerRef.current) return;

        // ایجاد چارت با تنظیمات ساده
        const chart = createChartFn(chartContainerRef.current, {
          layout: {
            background: { color: "#000000" },
            textColor: "#ffffff",
          },
          width: chartContainerRef.current.clientWidth,
          height: height,
        });

        console.log('Chart created successfully:', chart);
        console.log('Chart methods:', Object.getOwnPropertyNames(chart));
        console.log('addLineSeries method:', typeof chart.addLineSeries);

        // Try to add line series
        let series;
        if (typeof chart.addLineSeries === 'function') {
          series = chart.addLineSeries({
            color: periodColors[activePeriod],
            lineWidth: 2,
          });
          console.log('Line series added successfully:', series);
        } else {
          console.error('addLineSeries method not found on chart object');
          console.log('Available methods on chart:', Object.getOwnPropertyNames(chart));
          throw new Error('addLineSeries method not available');
        }

        // تنظیم داده اولیه
        const initialData = processedChartData[activePeriod] || [];
        console.log('Setting initial data:', initialData);
        
        if (initialData.length > 0) {
          series.setData(initialData);
          chart.timeScale().fitContent();
        }

        // ذخیره مراجع
        chartRef.current = chart;
        seriesRef.current = series;

        console.log('Chart setup completed successfully');

      } catch (err) {
        console.error('Error creating chart:', err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    createChart();

    // Cleanup when component unmounts
    return () => {
      isMounted = false;
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
        seriesRef.current = null;
      }
    };
  }, [height, periodColors, activePeriod, processedChartData]);

  // تغییر داده‌ها هنگام تغییر دوره
  useEffect(() => {
    if (chartRef.current && seriesRef.current && processedChartData[activePeriod]) {
      try {
        seriesRef.current.setData(processedChartData[activePeriod]);
        seriesRef.current.applyOptions({ color: periodColors[activePeriod] });
        chartRef.current.timeScale().fitContent();
        console.log(`Data updated for ${activePeriod}:`, processedChartData[activePeriod].length, 'points');
      } catch (error) {
        console.error('Error updating chart data:', error);
      }
    }
  }, [processedChartData, activePeriod, periodColors]);

  return (
    <Card>
      <CardHeader title={title || "نمودار قیمت"} />
      <CardContent>
        {/* دکمه‌های انتخاب دوره */}
        {showPeriodButtons && (
          <Box sx={{ mb: 2, display: 'flex', gap: 1, justifyContent: 'center' }}>
            {Object.keys(periodColors).map((period) => (
              <button
                key={period}
                onClick={() => changePeriod(period)}
                style={{
                  padding: "8px 16px",
                  backgroundColor: activePeriod === period ? periodColors[period] : "#333",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  fontSize: "14px",
                }}
              >
                {period}
              </button>
            ))}
          </Box>
        )}

        {/* نمایش اطلاعات debug */}
        <Box sx={{ mb: 2, textAlign: 'center', fontSize: '12px', color: '#666' }}>
          {isLoading && <Typography>در حال بارگذاری...</Typography>}
          {error && <Typography color="error">خطا در بارگذاری نمودار: {error}</Typography>}
          {!isLoading && !error && (
            <Typography>
              Debug: Data received | Active: {activePeriod} | Points: {processedChartData[activePeriod]?.length || 0}
              {processedChartData && Object.keys(processedChartData).length > 0 && (
                <> | Keys: {Object.keys(processedChartData).join(',')}</>
              )}
            </Typography>
          )}
        </Box>

        {/* محل نمایش نمودار */}
        <Box
          ref={chartContainerRef}
          sx={{
            width: "100%",
            height: `${height}px`,
            backgroundColor: "#000",
            borderRadius: 1,
          }}
        />
      </CardContent>
    </Card>
  );
};

export default PriceChart;
