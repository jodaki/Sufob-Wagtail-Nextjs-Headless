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

  // Colors matching TradingView style
  const periodColors = {
    "1D": "#2962FF",           // Blue
    "1W": "rgb(225, 87, 90)",  // Red
    "1M": "rgb(242, 142, 44)", // Orange
    "1Y": "rgb(164, 89, 209)", // Purple
  };

  // Enhanced sample data matching TradingView style
  const defaultData = {
    "1D": [
      { time: '2024-10-19', value: 26.19 },
      { time: '2024-10-22', value: 25.87 },
      { time: '2024-10-23', value: 25.83 },
      { time: '2024-10-24', value: 25.78 },
      { time: '2024-10-25', value: 25.82 },
      { time: '2024-10-26', value: 25.81 },
      { time: '2024-10-29', value: 25.82 },
      { time: '2024-10-30', value: 25.71 },
      { time: '2024-10-31', value: 25.82 },
      { time: '2024-11-01', value: 25.72 },
      { time: '2024-11-02', value: 25.74 },
      { time: '2024-11-05', value: 25.81 },
      { time: '2024-11-06', value: 25.75 },
      { time: '2024-11-07', value: 25.73 },
      { time: '2024-11-08', value: 25.75 },
      { time: '2024-11-09', value: 25.75 },
      { time: '2024-11-12', value: 25.76 },
      { time: '2024-11-13', value: 25.8 },
      { time: '2024-11-14', value: 25.77 },
      { time: '2024-11-15', value: 25.75 },
      { time: '2024-11-16', value: 25.75 },
      { time: '2024-11-19', value: 25.75 },
      { time: '2024-11-20', value: 25.72 },
      { time: '2024-11-21', value: 25.78 },
      { time: '2024-11-23', value: 25.72 },
      { time: '2024-11-26', value: 25.78 },
      { time: '2024-11-27', value: 25.85 },
      { time: '2024-11-28', value: 25.85 },
      { time: '2024-11-29', value: 25.55 },
      { time: '2024-11-30', value: 25.41 },
      { time: '2024-12-03', value: 25.41 },
      { time: '2024-12-04', value: 25.42 },
      { time: '2024-12-06', value: 25.33 },
      { time: '2024-12-07', value: 25.39 },
      { time: '2024-12-10', value: 25.32 },
      { time: '2024-12-11', value: 25.48 },
      { time: '2024-12-12', value: 25.39 },
      { time: '2024-12-13', value: 25.45 },
      { time: '2024-12-14', value: 25.52 },
      { time: '2024-12-17', value: 25.38 },
      { time: '2024-12-18', value: 25.36 },
      { time: '2024-12-19', value: 25.65 },
      { time: '2024-12-20', value: 25.7 },
      { time: '2024-12-21', value: 25.66 },
      { time: '2024-12-24', value: 25.66 },
      { time: '2024-12-26', value: 25.65 },
      { time: '2024-12-27', value: 25.66 },
      { time: '2024-12-28', value: 25.68 },
      { time: '2024-12-31', value: 25.77 },
    ],
    "1W": [
      { time: '2023-07-18', value: 26.1 },
      { time: '2023-07-25', value: 26.19 },
      { time: '2023-08-01', value: 26.24 },
      { time: '2023-08-08', value: 26.22 },
      { time: '2023-08-15', value: 25.98 },
      { time: '2023-08-22', value: 25.85 },
      { time: '2023-08-29', value: 25.98 },
      { time: '2023-09-05', value: 25.71 },
      { time: '2023-09-12', value: 25.84 },
      { time: '2023-09-19', value: 25.89 },
      { time: '2023-09-26', value: 25.65 },
      { time: '2023-10-03', value: 25.69 },
      { time: '2023-10-10', value: 25.67 },
      { time: '2023-10-17', value: 26.11 },
      { time: '2023-10-24', value: 25.8 },
      { time: '2023-10-31', value: 25.7 },
      { time: '2023-11-07', value: 25.4 },
      { time: '2023-11-14', value: 25.32 },
      { time: '2023-11-21', value: 25.48 },
      { time: '2023-11-28', value: 25.08 },
      { time: '2023-12-05', value: 25.06 },
      { time: '2023-12-12', value: 25.11 },
      { time: '2023-12-19', value: 25.34 },
      { time: '2023-12-26', value: 25.2 },
      { time: '2024-01-02', value: 25.33 },
      { time: '2024-01-09', value: 25.56 },
      { time: '2024-01-16', value: 25.32 },
      { time: '2024-01-23', value: 25.71 },
      { time: '2024-01-30', value: 25.85 },
      { time: '2024-02-06', value: 25.77 },
      { time: '2024-02-13', value: 25.94 },
      { time: '2024-02-20', value: 25.67 },
      { time: '2024-02-27', value: 25.6 },
      { time: '2024-03-06', value: 25.54 },
      { time: '2024-03-13', value: 25.84 },
      { time: '2024-03-20', value: 25.96 },
      { time: '2024-03-27', value: 25.9 },
      { time: '2024-04-03', value: 25.97 },
      { time: '2024-04-10', value: 26.0 },
      { time: '2024-04-17', value: 26.13 },
      { time: '2024-04-24', value: 26.02 },
      { time: '2024-05-01', value: 26.3 },
      { time: '2024-05-08', value: 26.27 },
      { time: '2024-05-15', value: 26.24 },
      { time: '2024-05-22', value: 26.02 },
      { time: '2024-05-29', value: 26.2 },
      { time: '2024-06-05', value: 26.12 },
      { time: '2024-06-12', value: 26.2 },
      { time: '2024-06-19', value: 26.46 },
      { time: '2024-06-26', value: 26.39 },
      { time: '2024-07-03', value: 26.52 },
      { time: '2024-07-10', value: 26.57 },
      { time: '2024-07-17', value: 26.65 },
      { time: '2024-07-24', value: 26.45 },
      { time: '2024-07-31', value: 26.37 },
      { time: '2024-08-07', value: 26.13 },
      { time: '2024-08-14', value: 26.21 },
      { time: '2024-08-21', value: 26.31 },
      { time: '2024-08-28', value: 26.33 },
      { time: '2024-09-04', value: 26.38 },
      { time: '2024-09-11', value: 26.38 },
      { time: '2024-09-18', value: 26.5 },
      { time: '2024-09-25', value: 26.39 },
      { time: '2024-10-02', value: 25.95 },
      { time: '2024-10-09', value: 26.15 },
      { time: '2024-10-16', value: 26.43 },
      { time: '2024-10-23', value: 26.22 },
      { time: '2024-10-30', value: 26.14 },
      { time: '2024-11-06', value: 26.08 },
      { time: '2024-11-13', value: 26.27 },
      { time: '2024-11-20', value: 26.3 },
      { time: '2024-11-27', value: 25.92 },
      { time: '2024-12-04', value: 26.1 },
      { time: '2024-12-11', value: 25.88 },
      { time: '2024-12-18', value: 25.82 },
      { time: '2024-12-25', value: 25.82 },
    ],
    "1M": [
      { time: '2020-12-01', value: 25.4 },
      { time: '2021-01-01', value: 25.5 },
      { time: '2021-02-01', value: 25.11 },
      { time: '2021-03-01', value: 25.24 },
      { time: '2021-04-02', value: 25.34 },
      { time: '2021-05-01', value: 24.82 },
      { time: '2021-06-01', value: 23.85 },
      { time: '2021-07-02', value: 23.24 },
      { time: '2021-08-01', value: 23.05 },
      { time: '2021-09-03', value: 22.26 },
      { time: '2021-10-01', value: 22.52 },
      { time: '2021-11-01', value: 20.84 },
      { time: '2021-12-03', value: 20.37 },
      { time: '2022-01-01', value: 23.9 },
      { time: '2022-02-01', value: 22.58 },
      { time: '2022-03-03', value: 21.74 },
      { time: '2022-04-01', value: 22.5 },
      { time: '2022-05-01', value: 22.38 },
      { time: '2022-06-02', value: 20.58 },
      { time: '2022-07-01', value: 20.6 },
      { time: '2022-08-01', value: 20.82 },
      { time: '2022-09-01', value: 17.5 },
      { time: '2022-10-01', value: 17.7 },
      { time: '2022-11-03', value: 15.52 },
      { time: '2022-12-01', value: 18.58 },
      { time: '2023-01-01', value: 15.4 },
      { time: '2023-02-02', value: 11.68 },
      { time: '2023-03-02', value: 14.89 },
      { time: '2023-04-01', value: 16.24 },
      { time: '2023-05-01', value: 18.33 },
      { time: '2023-06-01', value: 18.08 },
      { time: '2023-07-01', value: 20.07 },
      { time: '2023-08-03', value: 20.35 },
      { time: '2023-09-01', value: 21.53 },
      { time: '2023-10-01', value: 21.48 },
      { time: '2023-11-02', value: 20.28 },
      { time: '2023-12-01', value: 21.39 },
      { time: '2024-01-01', value: 22.0 },
      { time: '2024-02-01', value: 22.31 },
      { time: '2024-03-01', value: 22.82 },
      { time: '2024-04-01', value: 22.58 },
      { time: '2024-05-03', value: 21.02 },
      { time: '2024-06-01', value: 21.45 },
      { time: '2024-07-01', value: 22.42 },
      { time: '2024-08-02', value: 23.61 },
      { time: '2024-09-01', value: 24.4 },
      { time: '2024-10-01', value: 24.46 },
      { time: '2024-11-01', value: 23.64 },
      { time: '2024-12-01', value: 22.9 },
    ],
    "1Y": [
      { time: '2018-01-02', value: 24.89 },
      { time: '2019-01-01', value: 25.5 },
      { time: '2020-01-01', value: 23.9 },
      { time: '2021-01-01', value: 15.4 },
      { time: '2022-01-01', value: 22.0 },
      { time: '2023-01-03', value: 23.73 },
      { time: '2024-01-02', value: 24.84 },
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
        }).filter(item => item !== null)
        .sort((a, b) => new Date(a.time) - new Date(b.time)); // مرتب‌سازی صعودی بر اساس زمان
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

        // Simple import for lightweight-charts v4.1.3
        const { createChart } = await import("lightweight-charts");
        
        console.log('createChart function imported:', typeof createChart);

        if (!isMounted || !chartContainerRef.current) return;

        // ایجاد چارت با تنظیمات TradingView style
        const chart = createChart(chartContainerRef.current, {
          layout: {
            textColor: 'black',
            background: { type: 'solid', color: 'white' },
            fontSize: 12,
            fontFamily: '-apple-system, BlinkMacSystemFont, "Trebuchet MS", Roboto, Ubuntu, sans-serif',
          },
          width: chartContainerRef.current.clientWidth,
          height: height,
          grid: {
            vertLines: { 
              color: "#f0f3fa",
              style: 0,
              visible: true,
            },
            horzLines: { 
              color: "#f0f3fa", 
              style: 0,
              visible: true,
            },
          },
          crosshair: {
            mode: 1,
            vertLine: {
              color: "#9598A1",
              width: 1,
              style: 0,
              labelBackgroundColor: "#131722",
            },
            horzLine: {
              color: "#9598A1",
              width: 1,
              style: 0,
              labelBackgroundColor: "#131722",
            },
          },
          rightPriceScale: {
            borderColor: "#D6DCDE",
            textColor: "black",
            fontSize: 12,
            scaleMargins: {
              top: 0.1,
              bottom: 0.1,
            },
          },
          timeScale: {
            borderColor: "#D6DCDE",
            textColor: "black",
            fontSize: 12,
            timeVisible: true,
            secondsVisible: false,
          },
          watermark: {
            visible: false,
          },
          handleScroll: {
            mouseWheel: true,
            pressedMouseMove: true,
          },
          handleScale: {
            axisPressedMouseMove: true,
            mouseWheel: true,
            pinch: true,
          },
        });

        console.log('Chart created successfully:', chart);
        console.log('addLineSeries method:', typeof chart.addLineSeries);

        // اضافه کردن سری با استایل TradingView
        const series = chart.addLineSeries({
          color: periodColors[activePeriod],
          lineWidth: 2,
          lineStyle: 0, // solid line
          crosshairMarkerVisible: true,
          crosshairMarkerRadius: 4,
          crosshairMarkerBorderColor: periodColors[activePeriod],
          crosshairMarkerBackgroundColor: "white",
          lastValueVisible: true,
          priceLineVisible: true,
          priceLineColor: periodColors[activePeriod],
          priceLineWidth: 1,
          priceLineStyle: 2, // dashed
          baseLineVisible: false,
        });

        console.log('Line series created:', series);

        // تنظیم داده اولیه
        const initialData = processedChartData[activePeriod] || [];
        console.log('Setting initial data:', initialData);
        console.log('Data sorted check:', initialData.map(item => `${item.time}: ${item.value}`));
        
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
    <Card 
      sx={{ 
        background: "white",
        color: "black",
        border: "1px solid #e0e3eb",
        borderRadius: 2,
        boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
      }}
    >
      <CardHeader 
        title={title || "نمودار قیمت"} 
        sx={{
          color: "black",
          borderBottom: "1px solid #e0e3eb",
          "& .MuiCardHeader-title": {
            fontSize: "1.2rem",
            fontWeight: 500,
            textAlign: "center",
          }
        }}
      />
      <CardContent sx={{ padding: 2 }}>
        {/* دکمه‌های انتخاب دوره - TradingView Style */}
        {showPeriodButtons && (
          <Box sx={{ mb: 2, display: 'flex', gap: 1, justifyContent: 'center' }}>
            {Object.keys(periodColors).map((period) => (
              <button
                key={period}
                onClick={() => changePeriod(period)}
                style={{
                  fontFamily: '-apple-system, BlinkMacSystemFont, "Trebuchet MS", Roboto, Ubuntu, sans-serif',
                  fontSize: '16px',
                  fontStyle: 'normal',
                  fontWeight: '510',
                  lineHeight: '24px',
                  letterSpacing: '-0.32px',
                  padding: '8px 24px',
                  color: 'rgba(19, 23, 34, 1)',
                  backgroundColor: activePeriod === period ? 'rgba(209, 212, 220, 1)' : 'rgba(240, 243, 250, 1)',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  if (activePeriod !== period) {
                    e.target.style.backgroundColor = 'rgba(224, 227, 235, 1)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (activePeriod !== period) {
                    e.target.style.backgroundColor = 'rgba(240, 243, 250, 1)';
                  }
                }}
              >
                {period}
              </button>
            ))}
          </Box>
        )}

        {/* نمایش اطلاعات debug */}
        <Box sx={{ 
          mb: 2, 
          textAlign: 'center', 
          fontSize: '12px', 
          color: 'rgba(83, 91, 116, 0.8)',
          backgroundColor: "rgba(240, 243, 250, 0.5)",
          padding: 1.5,
          borderRadius: 1,
          border: "1px solid rgba(224, 227, 235, 0.8)",
        }}>
          {isLoading && (
            <Typography sx={{ color: "#2962FF" }}>
              🔄 در حال بارگذاری...
            </Typography>
          )}
          {error && (
            <Typography color="error" sx={{ color: "rgb(225, 87, 90)" }}>
              ❌ خطا در بارگذاری نمودار: {error}
            </Typography>
          )}
          {!isLoading && !error && (
            <Typography sx={{ color: "rgba(83, 91, 116, 1)" }}>
              📊 نمودار آماده | دوره فعال: <span style={{color: periodColors[activePeriod], fontWeight: 'bold'}}>{activePeriod}</span> | نقاط: <span style={{color: 'rgb(164, 89, 209)', fontWeight: 'bold'}}>{processedChartData[activePeriod]?.length || 0}</span>
              {processedChartData && Object.keys(processedChartData).length > 0 && (
                <> | دوره‌های موجود: <span style={{color: 'rgb(242, 142, 44)'}}>{Object.keys(processedChartData).join('، ')}</span></>
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
            backgroundColor: "white",
            borderRadius: 1,
            border: "1px solid #e0e3eb",
            overflow: "hidden",
            position: "relative",
          }}
        />
      </CardContent>
    </Card>
  );
};

export default PriceChart;
