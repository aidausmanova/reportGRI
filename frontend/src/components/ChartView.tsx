import React, { useEffect, useRef } from "react";
import * as echarts from "echarts";

interface BarChartItem {
  gri_disclosure: string,
  gri_disclosure_title: string,
  paragraph_count: number
}

interface RadarChartItem {
  gri_topic: string,
  gri_topic_title: string,
  value: number,
  description: string
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
  barChartData: Record<string, BarChartItem>;
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
    const disclosureMeta = {};
    const reportNames = Object.keys(barChartData);

    // reportNames.forEach((report) => {
    //   Object.keys(barChartData[report]).forEach((gri) => griSet.add(gri));
    // });
    reportNames.forEach((report) => {
      const disclosures = barChartData[report];
      for (const disclosureKey in disclosures) {
        disclosures[disclosureKey].forEach(item => {
          griSet.add(item.gri_disclosure);
          disclosureMeta[item.gri_disclosure] = item.gri_disclosure_title;
        });
      }
    });
    const griList = Array.from(griSet).sort();

    // const series = reportNames.map((report) => ({
    //   name: report,
    //   type: "bar",
    //   data: griList.map((gri) => barChartData[report][gri] || 0),
    // }));
    const series = reportNames.map((report) => {
      const data = griList.map((gri) => {
        const disclosureItems = barChartData[report];
        for (const disclosureKey in disclosureItems) {
          const match = disclosureItems[disclosureKey].find(item => item.gri_disclosure === gri);
          if (match) return match.paragraph_count;
        }
        return 0;
      });

      return {
        name: report,
        type: "bar",
        data,
      };
    });

    chart.setOption({
      // title: { text: "GRI Coverage Distribution", left: "center" },
      tooltip: {
        trigger: "axis",
        // axisPointer: { type: "shadow" },
        formatter: (params) => {
          return params
            .map((p) => {
              const title = disclosureMeta[p.axisValue] || "";
              return `<strong>${p.axisValue}</strong><br/>Title: ${title}<br/>Paragraphs: ${p.data}`;
            })
            .join("<br/><br/>");
        }
      },
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
    // const disclosureMeta = {};

    // const allTopics = new Set<string>();
    // reportNames.forEach((reportName) => {
    //   Object.keys(radarChartData[reportName]).forEach((topic) => {
    //     allTopics.add(topic);
    //   });
    // });

    // const sortedTopics = Array.from(allTopics).sort();
    // const indicator = sortedTopics.map((topic) => ({
    //   text: topic,
    //   max: 100 // % value (0–100)
    // }));

    const allTopics = [
      'General disclosure', 'Economic performance', 'Materials', 'Energy', 'Water',
      'Biodiversity', 'Emissions', 'Waste', 'Environmental compliance', 'Supplier assessment',
      'Employment', 'Employee safety', 'Training', 'Diversity', 'Communities',
      'Public policy', 'Customer safety', 'Customer privacy'
    ];

    const indicator = allTopics.map((topic) => ({
      text: topic,
      max: 100,
    }));

    const seriesData = reportNames.map((reportName) => {
      // const topicEntries = Object.entries(radarChartData[reportName] || {});
      // const topics = topicEntries.map(([_, entries]) => entries[0]);
      const topicMap = radarChartData[reportName] || {};
      const values = allTopics.map(topic => {
        const entries = topicMap[topic];
        if (entries && entries.length > 0) {
          return entries[0].value;
        } else {
          return 0; // Fill missing topics with 0%
        }
      });

      // const metadata = allTopics.map(topic => {
      //   const entries = topicMap[topic];
      //   return entries && entries.length > 0 ? entries[0] : {
      //     gri_topic: '',
      //     gri_topic_title: topic,
      //     value: 0,
      //     description: '',
      //   };
      // });
      const metadata = allTopics.flatMap(topic => {
        const entries = topicMap[topic];
        if (entries && entries.length > 0 && entries[0].value > 0) {
          return [entries[0]];
        } else {
          return [];
        }
      });

      return {
        // value: topics.map(t => t.value),
        value: values,
        name: reportName,
        metadata: metadata
      };
    });
    // const seriesData = reportNames.map(reportName => ({
    //   value: [
    //     radarChartData[reportName]["General disclosure"] || 0,
    //     radarChartData[reportName]["Economic performance"] || 0,
    //     radarChartData[reportName]["Materials"] || 0,
    //     radarChartData[reportName]["Energy"] || 0,
    //     radarChartData[reportName]["Water"] || 0,
    //     radarChartData[reportName]["Biodiversity"] || 0,
    //     radarChartData[reportName]["Emissions"] || 0,
    //     radarChartData[reportName]["Waste"] || 0,
    //     radarChartData[reportName]["Environmental compliance"] || 0,
    //     radarChartData[reportName]["Supplier assessment"] || 0,
    //     radarChartData[reportName]["Employment"] || 0,
    //     radarChartData[reportName]["Employee safety"] || 0,
    //     radarChartData[reportName]["Training"] || 0,
    //     radarChartData[reportName]["Diversity"] || 0,
    //     radarChartData[reportName]["Communities"] || 0,
    //     radarChartData[reportName]["Public policy"] || 0,
    //     radarChartData[reportName]["Customer safety"] || 0,
    //     radarChartData[reportName]["Customer privacy"] || 0
    //   ],
    //   name: reportName
    // }));

    const option = {
      // title: { text: "GRI standards focus", left: "center"},
      tooltip : {
        trigger: 'item',
        position: 'bottom',
        formatter: function (params) {
          const { value, name, data} = params;
          const metadata = data.metadata;

          let tooltipContent = `<strong>${name}</strong><br/>`;
            metadata.forEach((item) => {
              tooltipContent += `
                <div style="margin-bottom: 6px;">
                  <strong>${item.gri_topic}</strong> (${item.gri_topic_title}): ${item.value}%
                </div>
              `;
            });
          return tooltipContent
        }
      },
      legend: {show: true, orient : 'horizontal', x: "center", top: 10 , data: reportNames},
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
        // indicator: [
        //   {text: 'General disclosure', max: 100},
        //   {text: 'Economic performance', max: 100},
        //   {text: 'Materials', max: 100},
        //   {text: 'Energy', max: 100},
        //   {text: 'Water', max: 100},
        //   {text: 'Biodiversity', max: 100},
        //   {text: 'Emissions', max: 100},
        //   {text: 'Waste', max: 100},
        //   {text: 'Environmental compliance', max: 100},
        //   {text: 'Supplier assessment', max: 100},
        //   {text: 'Employment', max: 100},
        //   {text: 'Employee safety', max: 100},
        //   {text: 'Training', max: 100},
        //   {text: 'Diversity', max: 100},
        //   {text: 'Communities', max: 100},
        //   {text: 'Public policy', max: 100},
        //   {text: 'Customer safety', max: 100},
        //   {text: 'Customer privacy', max: 100}
        // ],
        indicator: indicator,
        center: ['50%', '50%'],
        radius: '60%',
        name: {
          textStyle: {
            fontSize: 18,
            fontWeight: "bold"
          }
        }
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
        // type: "scroll",
        orient: 'horizontal',
        // right: 10,
        top: 10,
        x:"center",
        // bottom: 20,
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
