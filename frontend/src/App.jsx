import { useState, useMemo } from "react";
import axios from "axios";

function App() {
  const [clientFile, setClientFile] = useState(null);
  const [perceptionFile, setPerceptionFile] = useState(null);
  const [results, setResults] = useState({
    false_claims: [] ,
    most_misperceived_claims: [] ,
    most_disputed_claims: []
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!clientFile || !perceptionFile) {
      alert("Please upload both CSV files");
      return;
    }

    const formData = new FormData();
    formData.append("claims_file", clientFile);
    formData.append("perceptions_file", perceptionFile);

    try {
      setLoading(true);

      const response = await axios.post(
        "http://127.0.0.1:8000/analyze_dataset",
        formData
      );

      setResults({
  false_claims: response.data.false_claims || [],
  most_misperceived_claims: response.data.most_misperceived_claims || [],
  most_disputed_claims: response.data.most_disputed_claims || []
});
    } catch (error) {
        console.error("FULL ERROR:", error);
        alert("Check console (F12) for error");
    } finally {
      setLoading(false);
    }
  };

  // KPIs
  const stats = useMemo(() => {
    const allClaims = [
  ...results.false_claims,
  ...results.most_misperceived_claims,
  ...results.most_disputed_claims
];

if (!allClaims.length) return null;

const avg =
  allClaims.reduce((sum, r) => sum + Number(r.disputability || 0), 0) /
  allClaims.length;

return {
  total: allClaims.length,
  avgDisputability: avg.toFixed(4),
};
  }, [results]);

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-6xl mx-auto bg-white shadow-xl rounded-2xl p-8">

        {/* Title */}
        <h1 className="text-3xl font-bold text-center mb-8">
          📊 News Prioritization Dashboard
        </h1>

        {/* Upload Section */}
        <div className="grid md:grid-cols-2 gap-6 mb-6">

          {/* Claims Upload */}
          <div className="border p-4 rounded-lg">
            <p className="font-medium mb-2">Claims CSV</p>

            <label className="flex items-center justify-between border rounded-lg p-3 cursor-pointer bg-gray-50 hover:bg-gray-100">
              <span>
                {clientFile ? clientFile.name : "No file selected"}
              </span>

              <span className="bg-blue-600 text-white px-3 py-1 rounded">
                Choose File
              </span>

              <input
                type="file"
                accept=".csv"
                className="hidden"
                onChange={(e) => setClientFile(e.target.files[0])}
              />
            </label>
          </div>

          {/* Perception Upload */}
          <div className="border p-4 rounded-lg">
            <p className="font-medium mb-2">Perceptions CSV</p>

            <label className="flex items-center justify-between border rounded-lg p-3 cursor-pointer bg-gray-50 hover:bg-gray-100">
              <span>
                {perceptionFile ? perceptionFile.name : "No file selected"}
              </span>

              <span className="bg-blue-600 text-white px-3 py-1 rounded">
                Choose File
              </span>

              <input
                type="file"
                accept=".csv"
                className="hidden"
                onChange={(e) => setPerceptionFile(e.target.files[0])}
              />
            </label>
          </div>

        </div>

        {/* Analyze Button */}
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold mb-8"
        >
          {loading ? "Analyzing..." : "Analyze Dataset"}
        </button>

        {/* KPI Cards */}
        {stats && (
          <div className="grid md:grid-cols-2 gap-6 mb-8">

            <div className="bg-blue-50 p-6 rounded-xl shadow">
              <h3 className="text-gray-600">Total Claims</h3>
              <p className="text-2xl font-bold">{stats.total}</p>
            </div>

            <div className="bg-green-50 p-6 rounded-xl shadow">
              <h3 className="text-gray-600">Avg Disputability</h3>
              <p className="text-2xl font-bold">
                {stats.avgDisputability}
              </p>
            </div>

          </div>
        )}

       {/* O1: False Claims */}
<h2 className="text-xl font-bold mt-6">False Claims (O1)</h2>
{results.false_claims.map((item, index) => (
  <div key={index} className="p-2 border mb-2">
    {item.claim}
  </div>
))}

{/* O2: Misperceived */}
<h2 className="text-xl font-bold mt-6">Most Misperceived (O2)</h2>
{results.most_misperceived_claims.map((item, index) => (
  <div key={index} className="p-2 border mb-2">
    {item.claim}
  </div>
))}

{/* O3: Disputed */}
<h2 className="text-xl font-bold mt-6">Most Disputed (O3)</h2>
{results.most_disputed_claims.map((item, index) => (
  <div key={index} className="p-2 border mb-2">
    {item.claim}
  </div>
))}

      </div>
    </div>
  );
}

export default App;