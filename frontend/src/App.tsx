import React, { useEffect, useState } from "react";
import ChartView from "./components/ChartView";
import logo from "/leuphana_logo.png";

const API_URL = "http://localhost:8000";

type ReportData = {
  bar_chart: Record<string, {gri_disclosure: string, gri_disclosure_title: string, paragraph_count: number}>;
  radar_chart: Record<string, {gri_topic: string, gri_topic_title: string, value: number, description: string}>;
  scatter_chart: Record<string, {disclosure: string, title: string, esg: string, completeness: number, materiality: number, comment: string}[]>;
};

function App() {
  const [industry, setIndustry] = useState("");
  const [industries, setIndustries] = useState<string[]>([]);
  const [existingReports, setExistingReports] = useState<string[]>([]);
  const [selectedExistingReports, setSelectedExistingReports] = useState<string[]>([]);
  const [myReports, setMyReports] = useState<string[]>([]);
  const [selectedMyReports, setSelectedMyReports] = useState<string[]>([]);
  // const [griLevel, setGriLevel] = useState<"l1" | "l2">("l1");
  // const [chartType, setChartType] = useState<"bar"| "radar" | "heatmap">("bar");
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  // const [selectedGRI, setSelectedGRI] = useState<string | null>(null);
  // const [selectedCell, setSelectedCell] = useState<null | { gri: string; section: string; score: number; gri_desc: string }>(null);


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
      // body: JSON.stringify({ report_names: allReports, gri_level: griLevel, chart: chartType }),
      body: JSON.stringify({ report_names: allReports }),
    })
      .then((res) => res.json())
      .then((data) => {
          console.log("Received data:", data);
          setReportData(data);
      })
      .finally(() => setIsLoading(false));
      // .then(setReportData)
  }, [selectedExistingReports, selectedMyReports]);

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

  // useEffect(() => {
  //   setSelectedGRI(null); // reset when user changes level
  // }, [griLevel]);

  const allowHeatmap = [...selectedExistingReports, ...selectedMyReports].length === 1;

  return (
    <>
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <aside className="w-80 bg-white border-r p-6 space-y-6">
        <div className="flex items-center space-x-3">
          {/* <img src={logo} alt="Leuphana Logo" className="h-10" /> */}
          <h1 className="text-2xl font-bold">Sustainability Report Analyzer</h1>
        </div>
        <p className="text-sm text-gray-500">
          This tool helps index your report to align with GRI framework. The report is also assessed by LLM on how well it covers disclosures.
        </p>

        <div>
          <label className="text-lg font-semibold text-gray-700 py-3">Existing reports</label>
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
          <div className="mt-3 space-y-1">
            {existingReports.map((rep) => (
              <label key={rep} className="block text-sm">
                <input
                  type="checkbox"
                  className="mr-2"
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

        {/* <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Reporting standard</label>
          <select
            className="w-full border px-3 py-2 rounded"
            value={griLevel}
            onChange={(e) => setGriLevel(e.target.value as "l1" | "l2")}
          >
            <option value="l1">GRI standard</option>
            <option value="l2">GRI disclosure</option>
          </select>
        </div> */}

        {/* <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Charts</label>
          <select
            className="w-full border px-3 py-2 rounded"
            value={chartType}
            onChange={(e) => setChartType(e.target.value as "bar" | "heatmap")}
          >
            <option value="bar">GRI focus and coverage</option>
            <option value="heatmap">GRI Heatmap</option>
          </select>
        </div> */}

        <button className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
          Display
        </button>

        <div className="pt-6 border-t">
        <label className="text-lg font-semibold text-gray-700 py-3">My Reports</label>
          <label className="block mb-1 text-sm text-gray-700">Upload report</label>
          <input type="file" accept="application/pdf" onChange={handleFileUpload} className="mb-2" />
          <p className="text-green-600 text-sm">Status: Processed</p>

          <label className="block text-sm font-medium text-gray-700 mt-4">Export assessment</label>
          <select className="w-full border px-2 py-1 rounded mt-1">
            <option value="json">JSON</option>
            <option value="csv">CSV</option>
          </select>
          <button className="mt-2 w-full bg-gray-200 text-sm text-gray-700 py-1 rounded hover:bg-gray-300">
            Export
          </button>
        </div>
      </aside>
      


      {/* Main chart display area */}
      <main className="flex-1 p-6 grid grid-cols-2 gap-6">
        {isLoading && (
          <div className="flex justify-center items-center py-6 col-span-2">
              <div className="w-10 h-10 border-4 border-blue-500 border-dashed rounded-full animate-spin"></div>
          </div>
        )}        
        
        {reportData && (          
          <ChartView
          barChartData={reportData?.bar_chart || {}}
          radarChartData={reportData?.radar_chart || null}
          scatterChartData={reportData?.scatter_chart || null}
          />          
        )}
        
      </main>
    </div>    

    </>
  );

//   console.log(reportData.heatmap_chart)
}

export default App;
