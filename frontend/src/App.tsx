import React, { useEffect, useState } from "react";
import ChartView from "./components/ChartView";
import logo from "/leuphana_logo.png";

const API_URL = "http://localhost:8000";

type ReportData = {
  bar_chart: Record<string, Record<string, number>>;
  radar_chart: Record<string, {Environmental: number, Social: number, Governance: number}>;
  heatmap_chart: { section: string; GRI_code: string; score: number; gri_desc: string }[];
  sections_by_gri: Record<string, { section: string; gri_desc: string }[]>;
};

function App() {
  const [industry, setIndustry] = useState("");
  const [industries, setIndustries] = useState<string[]>([]);
  const [existingReports, setExistingReports] = useState<string[]>([]);
  const [selectedExistingReports, setSelectedExistingReports] = useState<string[]>([]);
  const [myReports, setMyReports] = useState<string[]>([]);
  const [selectedMyReports, setSelectedMyReports] = useState<string[]>([]);
  const [griLevel, setGriLevel] = useState<"l1" | "l2">("l1");
  const [chartType, setChartType] = useState<"bar"| "radar" | "heatmap">("bar");
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedGRI, setSelectedGRI] = useState<string | null>(null);
  const [selectedCell, setSelectedCell] = useState<null | { gri: string; section: string; score: number; gri_desc: string }>(null);


  // console.log(reportData)

  // useEffect(() => {
  //     if (reportData && "radar_chart" in reportData) {
  //       console.log("Radar data:", reportData.radar_chart);
  //     } else {
  //       console.warn("Radar data missing or malformed");
  //     }
  // }, [reportData]);

  useEffect(() => {
    fetch(`${API_URL}/industries`)
      .then((res) => res.json())
      .then(setIndustries);

    fetch(`${API_URL}/my-reports`)
      .then((res) => res.json())
      .then(setMyReports);
  }, []);

  useEffect(() => {
    if (industry) {
      fetch(`${API_URL}/reports/${industry}`)
        .then((res) => res.json())
        .then(setExistingReports);
    }
  }, [industry]);

  useEffect(() => {
    const allReports = [...selectedExistingReports, ...selectedMyReports];
    if (allReports.length === 0) return;

    // console.log("Current chart type: ", chartType)

    setIsLoading(true);
    fetch(`${API_URL}/chart-data`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ report_names: allReports, gri_level: griLevel, chart: chartType }),
    })
      .then((res) => res.json())
      .then((data) => {
          console.log("Received data:", data);
          setReportData(data);
      })
      .finally(() => setIsLoading(false));
      // .then(setReportData)
  }, [selectedExistingReports, selectedMyReports, griLevel, chartType]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_URL}/upload`, {
      method: "POST",
      body: formData,
    });
    const result = await res.json();
    setMyReports(result.my_reports);
    setIsLoading(false);
  };

  useEffect(() => {
    setSelectedGRI(null); // reset when user changes level
  }, [griLevel]);

  const allowHeatmap = [...selectedExistingReports, ...selectedMyReports].length === 1;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <header className="flex items-center mb-10 p-4 bg-white rounded shadow-md">
        <img src={logo} alt="Leuphana Logo" className="h-12 mr-4" />
        <h1 className="text-3xl font-bold text-gray-800">Sustainability Reports Analyzer</h1>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-6">
        {/* Existing Reports Section */}
        <div className="bg-white p-5 rounded-lg shadow-md border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Existing Reports</h2>
          <label className="block mb-1 text-sm text-gray-700">Industry</label>
          <select
            className="w-full border p-2 rounded mb-3"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
          >
            <option value="">-- Select Industry --</option>
            {industries.map((ind) => (
              <option key={ind} value={ind}>{ind}</option>
            ))}
          </select>

          <div className="space-y-2">  
            {existingReports.map((rep) => (                
                <label key={rep} className="checkbox-label justify-evely text-grey-8 flex w-fit items-center gap-x-2 p-3 ms-2 text-sm font-medium">
                <input
                    type="checkbox"
                    className="w-4 h-4 gap-x-2 text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                    checked={selectedExistingReports.includes(rep)}
                    onChange={(e) => {
                    setSelectedExistingReports((prev) =>
                        e.target.checked ? [...prev, rep] : prev.filter((r) => r !== rep)
                    );
                    }}
                />                
                {rep}
                </label>                
            ))}
          </div>
        </div>

        {/* My Reports Section */}
          <div className="bg-white p-5 rounded-lg shadow-md border border-gray-200">
              <h2 className="text-xl font-semibold text-gray-700 mb-4">Your Reports</h2>
              <h2 className="block mb-1 text-sm text-gray-700">Upload your Reports</h2>
              <input type="file" accept="application/pdf" onChange={handleFileUpload}
                     className="block w-full text-sm text-gray-700 border border-gray-300 rounded-lg cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 file:bg-gray-100 file:border-none file:px-3 file:py-1"/>

              {myReports.map((rep) => (
                  <label key={rep}
                         className="checkbox-label justify-evely text-grey-8 flex w-fit items-center gap-x-2 p-3 ms-2 text-sm font-medium">
                      <input
                          type="checkbox"
                          className="w-4 h-4 gap-x-2 text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                          checked={selectedMyReports.includes(rep)}
                          onChange={(e) => {
                              setSelectedMyReports((prev) =>
                                  e.target.checked ? [...prev, rep] : prev.filter((r) => r !== rep)
                              );
                          }}
                      />
                      {rep}
                  </label>
              ))}

              {/*<h2 className="block mb-1 text-sm text-gray-700">Export alignment</h2>*/}
              {/*<div>*/}
              {/*    <label key={json}*/}
              {/*           className="checkbox-label justify-evely text-grey-8 flex w-fit items-center gap-x-2 p-3 ms-2 text-sm font-medium">*/}
              {/*    <input*/}
              {/*        type="checkbox"*/}
              {/*        className="w-4 h-4 gap-x-2 text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"*/}
              {/*    />*/}
              {/*    JSON*/}
              {/*    </label>*/}
              {/*        <select id="export" className="w-full px-4 py-2 border rounded mb-3">*/}
              {/*            <option value="json">JSON</option>*/}
              {/*            <option value="csv">CSV</option>*/}
              {/*        </select>*/}
              {/*        <button type="button">Export</button>*/}
              {/*</div>*/}

          </div>
      </div>

        {/* Display */}
        <div className="bg-white p-5 rounded-lg shadow-md border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">Display</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">GRI Level</label>
            <select
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={griLevel}
                onChange={(e) => setGriLevel(e.target.value as "l1" | "l2")}
            >
                <option value="l1">GRI standard</option>
                <option value="l2">GRI disclosure</option>
            </select>
            </div>
            <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Chart Type</label>
                <select
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={chartType}
                    onChange={(e) => setChartType(e.target.value as "bar" | "radar" | "heatmap")}
                    disabled={!allowHeatmap && chartType === "heatmap"}
                >
                    <option value="bar">GRI coverage distribution</option>
                    <option value="radar">Radar</option>
                    <option value="heatmap" disabled={!allowHeatmap}>Heatmap</option>
                </select>
            </div>
        </div>
      </div>

        {isLoading && (
        <div className="flex justify-center items-center py-6">
            <div className="w-10 h-10 border-4 border-blue-500 border-dashed rounded-full animate-spin"></div>
        </div>
        )}

      {reportData && (
        <div className="bg-white p-6 rounded-lg shadow-md mt-6">
            <ChartView
            barChartData={reportData?.bar_chart || {}}
            radarChartData={reportData?.radar_chart || null}
            heatmapData={reportData.heatmap_chart}
            sectionsByGRI={reportData.sections_by_gri}
            selectedGRI={selectedGRI}
            onGRISelect={setSelectedGRI}
            selectedCell={selectedCell}
            onHeatmapCellClick={setSelectedCell}
            showBarChart={chartType === "bar" || !allowHeatmap}
            showRadarChart={chartType === "radar" || !allowHeatmap}
            showHeatmap={chartType === "heatmap" && allowHeatmap}
            chartType={chartType}
            />
        </div>
      )}
    </div>
  );

//   console.log(reportData.heatmap_chart)
}

export default App;
