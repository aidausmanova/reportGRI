import React, { useEffect, useRef } from "react";
import * as echarts from "echarts";

interface RadarChartItem {
  Environmental: number;
  Social: number;
  Governance: number;
}

interface ScatterChatItem {
  disclosure: string,
  title: string,
  esg: "e" | "s" | "g",
  completeness: number,
  materiality: number,
  comment: string
}

interface ChartViewProps {
  barChartData: Record<string, Record<string, number>>; // report -> GRI -> count
  radarChartData: Record<string, RadarChartItem>;
  scatterChartData: Record<string, ScatterChatItem[]>
}

const ChartView: React.FC<ChartViewProps> = ({
  barChartData,
  radarChartData,
    scatterChartData
}) => {
  const barRef = useRef<HTMLDivElement>(null);
  const radarRef = useRef<HTMLDivElement>(null);
  const scatterRef = useRef<HTMLDivElement>(null);
  
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
      yAxis: { type: "value", name: "Paragraph count", position: 'left'},
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
        radarChartData[reportName]["General disclosure"] || 0,
        radarChartData[reportName]["Economic performance"] || 0,
        radarChartData[reportName]["Materials"] || 0,
        radarChartData[reportName]["Energy"] || 0,
        radarChartData[reportName]["Water"] || 0,
        radarChartData[reportName]["Biodiversity"] || 0,
        radarChartData[reportName]["Emissions"] || 0,
        radarChartData[reportName]["Waste"] || 0,
        radarChartData[reportName]["Environmental compliance"] || 0,
        radarChartData[reportName]["Supplier assessment"] || 0,
        radarChartData[reportName]["Employment"] || 0,
        radarChartData[reportName]["Employee safety"] || 0,
        radarChartData[reportName]["Training"] || 0,
        radarChartData[reportName]["Diversity"] || 0,
        radarChartData[reportName]["Communities"] || 0,
        radarChartData[reportName]["Public policy"] || 0,
        radarChartData[reportName]["Customer safety"] || 0,
        radarChartData[reportName]["Customer privacy"] || 0
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
        areaStyle: {
          opacity: 0.2
        },
        options: {
          scales: {r: {grid: {circular: true}}},
          elements: {line: {borderWidth: 3}}
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

  // Render Scatter Chart
  useEffect(() => {
    if (!scatterChartData || !scatterRef.current) return;

    const chart = echarts.init(scatterRef.current);
    const reportNames = Object.keys(scatterChartData);

    const esgColorMap: Record<"e" | "s" | "g", string> = {
      e: "#4CAF50", // green
      s: "#2196F3", // blue
      g: "#FFC107", // amber
    };
    const wrapText = (text: string, maxLineLength: number = 50): string => {
      if (!text) return "";
      const words = text.split(" ");
      let lines: string[] = [];
      let currentLine = "";

      words.forEach(word => {
        if ((currentLine + word).length > maxLineLength) {
          lines.push(currentLine.trim());
          currentLine = "";
        }
        currentLine += word + " ";
      });
      if (currentLine.trim()) lines.push(currentLine.trim());

      return lines.join("<br/>");
    };

    function jitter(value: number, amount = 0.1) {
        return value + (Math.random() - 0.5) * amount;
      }
    const series = reportNames.map(report => ({
      name: report,
      type: "scatter",
      data: scatterChartData[report].map(item => ({
        value: [jitter(item.materiality), jitter(item.completeness)],
        name: item.disclosure,
        title: item.title,
        comment: item.comment,
        label: {
          // show: true,
          // formatter: item.title,
          position: "top",
          fontSize: 10,
          color: esgColorMap[item.esg]
        },
        itemStyle: {
          color: esgColorMap[item.esg],
        }
      })),
    }));
    // ${data.comment ? `Comment: ${data.comment}` : ""
    const option = {
      tooltip: {
        trigger: "item",
        // confine: true,
        position: 'bottom',
        formatter: (params: any) => {
          const { data } = params;
          const wrappedComment = data.comment ? wrapText(data.comment) : "";
          return `
            <strong>${data.name}</strong><br/>
            Title: ${data.title}<br/>
            Materiality: ${data.value[0].toFixed(2)}<br/>
            Completeness: ${data.value[1].toFixed(2)}<br/>
            ${wrappedComment ? `${wrappedComment}` : ""}
          `;
        }
      },
      legend: {
        type: "scroll",
        orient: 'vertical',
        right: 10,
        top: 20,
        bottom: 20,
        itemWidth: 10,
        itemHeight: 20,
        pageIconSize: 10,
        pageTextStyle: {
          color: '#888',
          fontSize: 10
        },
        textStyle: {
          fontSize: 12,
          lineHeight: 16,
        },
        data: reportNames },
      toolbox: {
        show: true,
        feature: {
          dataZoom: { yAxisIndex: "none" },
          dataView: { readOnly: false },
          restore: {},
          saveAsImage: {}
        }
      },
      xAxis: {
        name: "Materiality",
        min: 0,
        max: 10,
        type: "value",
      },
      yAxis: {
        name: "Completeness",
        min: 0,
        max: 10,
        type: "value",
      },
      series
    };

  chart.setOption(option);

  const resize = () => chart.resize();
  window.addEventListener("resize", resize);
  return () => {
    window.removeEventListener("resize", resize);
    chart.dispose();
  };
  }, [scatterChartData]);

  return (
    <>
    <div className="bg-white rounded shadow p-4">
      <h2 className="text-lg font-semibold text-gray-700 mb-2">Completeness vs Materiality</h2>
      <div className="h-96 bg-gray-100 flex items-center justify-center">
        <div ref={scatterRef} className="w-full h-96" />
      </div>
    </div>
    <div className="bg-white rounded shadow p-4">
      <h2 className="text-lg font-semibold text-gray-700 mb-2">Topic focus</h2>
      <div className="h-96 bg-gray-100 flex items-center justify-center">
        <div ref={radarRef} className="w-full h-96" />
      </div>
    </div>
    <div className="bg-white rounded shadow p-4 col-span-2">
      <h2 className="text-lg font-semibold text-gray-700 mb-2">Paragraphs per disclosure</h2>
      <div className="h-96 bg-gray-100 flex items-center justify-center">
        <div ref={barRef} className="w-full h-96" />        
      </div>
    </div>
    

    </>
  );
};

export default ChartView;
