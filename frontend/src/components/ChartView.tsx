import React, { useEffect, useRef } from "react";
import * as echarts from "echarts";

interface HeatmapItem {
  section: string;
  GRI_code: string;
  score: number;
  gri_desc: string;
}

interface SectionDetail {
  section: string;
  gri_desc: string;
}

interface ChartViewProps {
  barChartData: Record<string, Record<string, number>>; // report -> GRI -> count
  heatmapData: HeatmapItem[];
  sectionsByGRI: Record<string, SectionDetail[]>;
  selectedGRI: string | null;
  onGRISelect: (gri: string | null) => void;
  selectedCell: HeatmapItem | null;
  onHeatmapCellClick: (info: HeatmapItem) => void;
  showBarChart: boolean;
  showHeatmap: boolean;
}

const ChartView: React.FC<ChartViewProps> = ({
  barChartData,
  heatmapData,
  sectionsByGRI,
  selectedGRI,
  onGRISelect,
  selectedCell,
  onHeatmapCellClick,
  showBarChart,
  showHeatmap,
}) => {
  const barRef = useRef<HTMLDivElement>(null);
  const heatmapRef = useRef<HTMLDivElement>(null);

  // Render Bar Chart
  useEffect(() => {
    if (!showBarChart || !barRef.current) return;
    const chart = echarts.init(barRef.current);
    const griSet = new Set<string>();
    const reportNames = Object.keys(barChartData);

    reportNames.forEach((report) => {
      Object.keys(barChartData[report]).forEach((gri) => griSet.add(gri));
    });
    const griList = Array.from(griSet);

    const series = reportNames.map((report) => ({
      name: report,
      type: "bar",
      data: griList.map((gri) => barChartData[report][gri] || 0),
    }));

    chart.setOption({
      title: { text: "GRI Distribution", left: "center" },
      tooltip: { trigger: "axis" },
      legend: { top: 30 },
      xAxis: { type: "category", data: griList },
      yAxis: { type: "value" },
      series,
    });

    chart.off("click");
    chart.on("click", (params: any) => {
      onGRISelect(params.name === selectedGRI ? null : params.name);
    });

    const resize = () => chart.resize();
    window.addEventListener("resize", resize);
    return () => {
      window.removeEventListener("resize", resize);
      chart.dispose();
    };
  }, [barChartData, showBarChart]);

  // Render Heatmap
  useEffect(() => {
    if (!showHeatmap || !heatmapRef.current || !Array.isArray(heatmapData) || heatmapData.length === 0) return;

    const chart = echarts.init(heatmapRef.current);

    const sections = Array.from(new Set(heatmapData.map((d) => d.section)));
    const gris = Array.from(new Set(heatmapData.map((d) => d.GRI_code)));

    const data = heatmapData.map((item) => [
      gris.indexOf(item.GRI_code),
      sections.indexOf(item.section),
      item.score,
    ]);

    chart.setOption({
      title: { text: "Matching Score Heatmap", left: "center" },
      tooltip: {
        formatter: (params: any) => {
          const i = heatmapData.find(
            (d) => d.GRI_code === gris[params.value[0]] && d.section === sections[params.value[1]]
          );
          return `GRI: ${i?.GRI_code}<br/>Desc: ${i?.gri_desc}<br/>Section: ${i?.section}<br/>Score: ${i?.score}`;
        },
      },
      xAxis: { type: "category", data: gris, name: "GRI Code" },
      yAxis: { type: "category", data: sections, name: "Section" },
      visualMap: {
        min: 0,
        max: 1,
        calculable: true,
        orient: "horizontal",
        left: "center",
        bottom: 20,
      },
      series: [
        {
          name: "Score",
          type: "heatmap",
          data,
          emphasis: { itemStyle: { borderColor: "#fff", borderWidth: 1 } },
        },
      ],
    });

    chart.off("click");
    chart.on("click", (params: any) => {
      const match = heatmapData.find(
        (d) => d.GRI_code === gris[params.value[0]] && d.section === sections[params.value[1]]
      );
      if (match) onHeatmapCellClick(match);
    });

    const resize = () => chart.resize();
    window.addEventListener("resize", resize);
    return () => {
      window.removeEventListener("resize", resize);
      chart.dispose();
    };
  }, [heatmapData, showHeatmap, onHeatmapCellClick]);

  return (
    <div className="space-y-6">
      {showBarChart && <div ref={barRef} className="w-full h-96" />}
      {selectedGRI && sectionsByGRI[selectedGRI] && (
        <div className="bg-white p-4 rounded shadow">
          <h3 className="text-lg font-semibold mb-2">
            Sections for GRI: {selectedGRI}
          </h3>
            <table className="min-w-full border text-sm text-gray-700">
            <thead>
                <tr className="bg-gray-100">
                <th className="text-left px-4 py-2 border-b">Section</th>
                <th className="text-left px-4 py-2 border-b">GRI Description</th>
                </tr>
            </thead>
            <tbody>
                {sectionsByGRI[selectedGRI].map((item, idx) => (
                <tr key={idx} className="hover:bg-blue-50 transition-colors">
                    <td className="px-4 py-2 border-b">{item.section}</td>
                    <td className="px-4 py-2 border-b">{item.gri_desc}</td>
                </tr>
                ))}
            </tbody>
            </table>          
        </div>
      )}
      {showHeatmap && <div ref={heatmapRef} className="w-full h-[500px]" />}
      {selectedCell && (
        <div className="bg-white p-4 rounded shadow">
          <h3 className="text-lg font-semibold mb-2">Heatmap Selection</h3>
          <p><strong>GRI:</strong> {selectedCell.GRI_code}</p>
          <p><strong>Section:</strong> {selectedCell.section}</p>
          <p><strong>Score:</strong> {selectedCell.score}</p>
          <p><strong>Description:</strong> {selectedCell.gri_desc}</p>
        </div>
      )}
    </div>
  );
};

export default ChartView;
