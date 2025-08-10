"use client";

import React, { useEffect, useRef, useState } from "react";

const PriceChart = ({ data = null, height = 350 }) => {
  const chartContainerRef = useRef(null);
  const [lineSeries, setLineSeries] = useState(null);
  const [chart, setChart] = useState(null);

  // داده پیش‌فرض
  const defaultData = {
    dayData: [
      { time: "2024-01-01", value: 54540 },
      { time: "2024-01-02", value: 53920 },
      { time: "2024-01-03", value: 54200 },
      { time: "2024-01-04", value: 53800 },
      { time: "2024-01-05", value: 54100 },
      { time: "2024-01-06", value: 54300 },
      { time: "2024-01-07", value: 53950 },
      { time: "2024-01-08", value: 54180 },
      { time: "2024-01-09", value: 54050 },
      { time: "2024-01-10", value: 54320 },
    ],
    weekData: [
      { time: "2024-01-01", value: 54540 },
      { time: "2024-01-08", value: 53920 },
      { time: "2024-01-15", value: 54200 },
      { time: "2024-01-22", value: 53800 },
      { time: "2024-01-29", value: 54100 },
    ],
    monthData: [
      { time: "2024-01-01", value: 54540 },
      { time: "2024-02-01", value: 53920 },
      { time: "2024-03-01", value: 54200 },
      { time: "2024-04-01", value: 53800 },
    ],
    yearData: [
      { time: "2020-01-01", value: 45000 },
      { time: "2021-01-01", value: 48000 },
      { time: "2022-01-01", value: 52000 },
      { time: "2023-01-01", value: 50000 },
      { time: "2024-01-01", value: 54540 },
    ],
  };

  const chartData = data || defaultData;

  // ساخت چارت
  useEffect(() => {
    if (!chartContainerRef.current) return;

    import("lightweight-charts").then((LightweightCharts) => {
      const chartInstance = LightweightCharts.createChart(
        chartContainerRef.current,
        {
          width: chartContainerRef.current.offsetWidth || 600,
          height,
          layout: { background: { color: "#000" }, textColor: "#fff" },
          grid: {
            vertLines: { color: "#333" },
            horzLines: { color: "#333" },
          },
          rightPriceScale: { borderColor: "#666" },
          timeScale: { borderColor: "#666" },
        }
      );

      const series = chartInstance.addLineSeries({
        color: "#dc3545",
        lineWidth: 2,
      });

      series.setData(chartData.dayData);
      chartInstance.timeScale().fitContent();

      setChart(chartInstance);
      setLineSeries(series);
    });

    // پاک‌سازی
    return () => {
      if (chart) chart.remove();
    };
  }, []);

  // تغییر بازه زمانی
  const changePeriod = (newData, color) => {
    if (!lineSeries || !chart) return;
    lineSeries.setData(newData);
    lineSeries.applyOptions({ color });
    chart.timeScale().fitContent();
  };

  return (
    <div className="bg-black rounded p-2">
      <div
        ref={chartContainerRef}
        style={{ height: height, minHeight: 200 }}
      />
      <div className="flex gap-2 justify-center mt-3">
        <button
          onClick={() => changePeriod(chartData.dayData, "#dc3545")}
          className="px-4 py-2 bg-gray-700 text-white rounded"
        >
          1D
        </button>
        <button
          onClick={() => changePeriod(chartData.weekData, "#28a745")}
          className="px-4 py-2 bg-gray-700 text-white rounded"
        >
          1W
        </button>
        <button
          onClick={() => changePeriod(chartData.monthData, "#ffc107")}
          className="px-4 py-2 bg-gray-700 text-white rounded"
        >
          1M
        </button>
        <button
          onClick={() => changePeriod(chartData.yearData, "#17a2b8")}
          className="px-4 py-2 bg-gray-700 text-white rounded"
        >
          1Y
        </button>
      </div>
    </div>
  );
};

export default PriceChart;
