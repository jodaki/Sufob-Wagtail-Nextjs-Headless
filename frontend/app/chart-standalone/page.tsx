"use client";

import React, { useEffect, useRef } from 'react';

const TestChart = () => {
  const chartContainerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Clear previous chart
    chartContainerRef.current.innerHTML = '';

    const containerWidth = chartContainerRef.current.offsetWidth || 600;
    const containerHeight = chartContainerRef.current.offsetHeight || 300;

    // Sample data for different time periods - using more realistic price movements
    const dayData = [
      { time: '2024-01-01', value: 26.19 },
      { time: '2024-01-02', value: 25.87 },
      { time: '2024-01-03', value: 25.83 },
      { time: '2024-01-04', value: 25.78 },
      { time: '2024-01-05', value: 25.82 },
      { time: '2024-01-06', value: 25.81 },
      { time: '2024-01-07', value: 25.82 },
      { time: '2024-01-08', value: 25.71 },
      { time: '2024-01-09', value: 25.82 },
      { time: '2024-01-10', value: 25.72 },
      { time: '2024-01-11', value: 25.74 },
      { time: '2024-01-12', value: 25.81 },
      { time: '2024-01-13', value: 25.75 },
      { time: '2024-01-14', value: 25.73 },
      { time: '2024-01-15', value: 25.75 },
    ];

    const weekData = [
      { time: '2024-01-01', value: 26.1 },
      { time: '2024-01-08', value: 26.19 },
      { time: '2024-01-15', value: 26.24 },
      { time: '2024-01-22', value: 26.22 },
      { time: '2024-01-29', value: 25.98 },
      { time: '2024-02-05', value: 25.85 },
      { time: '2024-02-12', value: 25.98 },
      { time: '2024-02-19', value: 25.71 },
      { time: '2024-02-26', value: 25.84 },
      { time: '2024-03-05', value: 25.89 },
    ];

    const monthData = [
      { time: '2024-01-01', value: 25.4 },
      { time: '2024-02-01', value: 25.5 },
      { time: '2024-03-01', value: 25.11 },
      { time: '2024-04-01', value: 25.24 },
      { time: '2024-05-01', value: 25.34 },
      { time: '2024-06-01', value: 24.82 },
      { time: '2024-07-01', value: 23.85 },
      { time: '2024-08-01', value: 24.24 },
    ];

    const yearData = [
      { time: '2019-01-01', value: 24.89 },
      { time: '2020-01-01', value: 25.5 },
      { time: '2021-01-01', value: 23.9 },
      { time: '2022-01-01', value: 15.4 },
      { time: '2023-01-01', value: 22.0 },
      { time: '2024-01-01', value: 23.73 },
      { time: '2025-01-01', value: 24.84 },
    ];

    console.log('Chart data prepared:', { dayData, weekData, monthData, yearData });

    // Import chart library dynamically
    import('lightweight-charts').then(LightweightCharts => {
      if (!chartContainerRef.current) return;

      console.log('Creating chart with dimensions:', containerWidth, 'x', containerHeight);

      const chart = LightweightCharts.createChart(chartContainerRef.current, {
        width: containerWidth,
        height: containerHeight,
        layout: { 
          background: { color: 'white' }, 
          textColor: 'black' 
        },
        grid: { 
          vertLines: { color: '#f0f0f0' }, 
          horzLines: { color: '#f0f0f0' } 
        },
        rightPriceScale: { borderColor: '#ccc' },
        timeScale: { borderColor: '#ccc' },
      });

      const lineSeries = chart.addSeries(LightweightCharts.LineSeries, {
        color: '#2962FF',
        lineWidth: 2,
      });

      console.log('Line series created, setting initial data...');

      // Set initial data
      lineSeries.setData(dayData);
      chart.timeScale().fitContent();

      console.log('Initial data set, creating buttons...');

      // Create buttons for period selection
      const buttonsContainer = document.createElement('div');
      buttonsContainer.style.display = 'flex';
      buttonsContainer.style.gap = '8px';
      buttonsContainer.style.marginTop = '10px';
      buttonsContainer.style.justifyContent = 'center';

      const periods = [
        { label: '1D', data: dayData, color: '#2962FF' },
        { label: '1W', data: weekData, color: 'rgb(225, 87, 90)' },
        { label: '1M', data: monthData, color: 'rgb(242, 142, 44)' },
        { label: '1Y', data: yearData, color: 'rgb(164, 89, 209)' },
      ];

      periods.forEach(period => {
        const button = document.createElement('button');
        button.innerText = period.label;
        button.style.padding = '8px 16px';
        button.style.border = '1px solid #ccc';
        button.style.borderRadius = '4px';
        button.style.backgroundColor = '#f8f9fa';
        button.style.cursor = 'pointer';
        button.style.fontSize = '14px';

        button.addEventListener('click', () => {
          console.log('Button clicked:', period.label, 'Data:', period.data);
          lineSeries.setData(period.data);
          lineSeries.applyOptions({ color: period.color });
          chart.timeScale().fitContent();
        });

        buttonsContainer.appendChild(button);
      });

      chartContainerRef.current.appendChild(buttonsContainer);
      console.log('Chart setup complete!');
    }).catch(error => {
      console.error('Error loading lightweight-charts:', error);
    });
  }, []);

  return (
    <html lang="fa" dir="rtl">
      <head>
        <title>تست چارت TradingView</title>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>{`
          body {
            margin: 0;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
          }
          .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          }
          h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2rem;
          }
          .chart-container {
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 15px;
            background: white;
          }
        `}</style>
      </head>
      <body>
        <div className="container">
          <h1>تست چارت TradingView - بدون Backend</h1>
          <div className="chart-container">
            <div 
              ref={chartContainerRef} 
              style={{ height: 350, minHeight: 200, width: '100%' }}
            />
          </div>
        </div>
      </body>
    </html>
  );
};

export default TestChart;
