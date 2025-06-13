import React, { useEffect, useRef } from "react";
import * as echarts from "echarts";

interface RadarChartItem {
  Environmental: number;
  Social: number;
  Governance: number;
}

interface ChartViewProps {
  barChartData: Record<string, Record<string, number>>; // report -> GRI -> count
  radarChartData: Record<string, RadarChartItem>;
}

const ChartView: React.FC<ChartViewProps> = ({
  barChartData,
  radarChartData
}) => {
  const barRef = useRef<HTMLDivElement>(null);
  const radarRef = useRef<HTMLDivElement>(null);
  
  // Render Bar Chart
  useEffect(() => {
    if (!barRef.current) return;
    const chart = echarts.init(barRef.current);
    const griSet = new Set<string>();
    const reportNames = Object.keys(barChartData);

    reportNames.forEach((report) => {
      Object.keys(barChartData[report]).forEach((gri) => griSet.add(gri));
    });
    const griList = Array.from(griSet).sort();

    const series = reportNames.map((report) => ({
      name: report,
      type: "bar",
      data: griList.map((gri) => barChartData[report][gri] || 0),
    }));

    chart.setOption({
      // title: { text: "GRI Coverage Distribution", left: "center" },
      tooltip: { trigger: "axis" },
      legend: { top: 30 },
      toolbox: {
            show : true,
            feature : {
                mark : {show: true},
                dataView : {show: true, readOnly: false},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
      xAxis: { type: "category", data: griList, axisLabel: {rotate: 45,interval: 0} },
      yAxis: { type: "value"},
      series,
    });   

    const resize = () => chart.resize();
    window.addEventListener("resize", resize);
    return () => {
      window.removeEventListener("resize", resize);
      chart.dispose();
    };
  }, [barChartData]);

  // Render Radar Chart
  useEffect(() => {
    if (!radarChartData) return;
    const chart = echarts.init(radarRef.current);
    const reportNames = Object.keys(radarChartData);

    const seriesData = reportNames.map(reportName => ({
      value: [
        radarChartData[reportName]["Environmental"] || 0,
        radarChartData[reportName]["Social"] || 0,
        radarChartData[reportName]["Governance"] || 0
      ],
      name: reportName
    }));    

    const option = {
      // title: { text: "GRI standards focus", left: "center"},
      tooltip : {trigger: 'axis'},
      legend: {orient : 'vertical', right: 100, y:"center", data: reportNames},
      toolbox: {
        show : true,
        feature : {
          mark : {show: true},
          dataView : {show: true, readOnly: false},
          restore : {show: true},
          saveAsImage : {show: true}
        }
      },
      polar: {
        indicator: [
            // { text: 'Environmental', max: 100 },
            // { text: 'Social', max: 100 },
            // { text: 'Governance', max: 100 },
          {text: 'General disclosure'},
          {text: 'Economic performance'},
          {text: 'Materials'},
          {text: 'Energy'},
          {text: 'Water'},
          {text: 'Biodiversity'},
          {text: 'Emissions'},
          {text: 'Waste'},
          {text: 'Environmental compliance'},
          {text: 'Supplier assessment'},
          {text: 'Employment'},
          {text: 'Employee safety'},
          {text: 'Training'},
          {text: 'Diversity'},
          {text: 'Communities'},
          {text: 'Public policy'},
          {text: 'Customer safety'},
          {text: 'Customer privacy'}
        ],
        center: ['50%', '50%'],
        radius: '60%',
      },
      calculable : true,
      series: [{
        name: "GRI coverage",
        type: 'radar',
        // itemStyle: {normal: {areaStyle: {type: 'default'}}},
        data: seriesData,
        options: {
          scales: {
            r: {
              grid: {
                circular: true,
              },
            },
          },
          elements: {
            line: {
              borderWidth: 3
            }
          }
        },
      }]
    };

    chart.setOption(option);
   
    console.log(radarChartData)

    const resize = () => chart.resize();
    window.addEventListener("resize", resize);
    return () => {
      window.removeEventListener("resize", resize);
      chart.dispose();
    };
  }, [radarChartData]);


  return (
    <>
    <div className="bg-white rounded shadow p-4">
      <h2 className="text-lg font-semibold text-gray-700 mb-2">Completeness vs Materiality</h2>
      <div className="h-96 bg-gray-100 flex items-center justify-center">Chart Placeholder 1</div>
    </div>
    <div className="bg-white rounded shadow p-4">
      <h2 className="text-lg font-semibold text-gray-700 mb-2">Topic focus</h2>
      <div className="h-96 bg-gray-100 flex items-center justify-center">
        <div ref={radarRef} className="w-full h-96" />
      </div>
    </div>
    <div className="bg-white rounded shadow p-4 col-span-2">
      <h2 className="text-lg font-semibold text-gray-700 mb-2">Coverage distribution</h2>
      <div className="h-96 bg-gray-100 flex items-center justify-center">
        <div ref={barRef} className="w-full h-96" />        
      </div>
    </div>
    

    </>
  );
};

export default ChartView;
