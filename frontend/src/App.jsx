import { useState, useMemo } from "react";
import axios from "axios";

function App() {
  const [clientFile, setClientFile] = useState(null);
  const [perceptionFile, setPerceptionFile] = useState(null);
  const [results, setResults] = useState({
    false_claims: [],
    most_misperceived_claims: [],
    most_disputed_claims: [],
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
        most_misperceived_claims:
          response.data.most_misperceived_claims || [],
        most_disputed_claims:
          response.data.most_disputed_claims || [],
      });
    } catch (error) {
      console.error("FULL ERROR:", error);
      alert("Check console (F12) for error");
    } finally {
      setLoading(false);
    }
  };

  // ✅ KPI Calculation
  const stats = useMemo(() => {
    const allClaims = [
      ...results.false_claims,
      ...results.most_misperceived_claims,
      ...results.most_disputed_claims,
    ];

    if (!allClaims.length) return null;

    const avg =
      allClaims.reduce(
        (sum, r) => sum + Number(r.disputability || 0),
        0
      ) / allClaims.length;

    return {
      total: allClaims.length,
      avgDisputability: avg.toFixed(4),
    };
  }, [results]);

  // ✅ Reusable Table
  const renderTable = (title, data) => (
    <div className="mt-6">
      <h2 className="text-xl font-bold mb-2">{title}</h2>

      {data.length === 0 ? (
        <p className="text-gray-500">No data available</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border border-gray-300 rounded-lg">
            <thead className="bg-gray-200">
              <tr>
                <th className="p-2 border">ID</th>
                <th className="p-2 border">Claim</th>
                <th className="p-2 border">Truth</th>
                <th className="p-2 border">TPB</th>
                <th className="p-2 border">Disputability</th>
              </tr>
            </thead>

            <tbody>
              {data.map((item, index) => (
                <tr
                  key={index}
                  className={`text-center ${
                    index % 2 === 0 ? "bg-gray-50" : ""
                  }`}
                >
                  <td className="p-2 border">{item.claim_id}</td>

                  <td className="p-2 border text-left">
                    {item.claim}
                  </td>

                  <td
                    className={`p-2 border font-semibold ${
                      item.predicted_truth === "False"
                        ? "text-red-600"
                        : "text-green-600"
                    }`}
                  >
                    {item.predicted_truth}
                  </td>

                  <td className="p-2 border">
                    {item.predicted_TPB}
                  </td>

                  <td className="p-2 border">
                    {Number(item.disputability).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

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
                onChange={(e) =>
                  setClientFile(e.target.files[0])
                }
              />
            </label>
          </div>

          {/* Perception Upload */}
          <div className="border p-4 rounded-lg">
            <p className="font-medium mb-2">
              Perceptions CSV
            </p>

            <label className="flex items-center justify-between border rounded-lg p-3 cursor-pointer bg-gray-50 hover:bg-gray-100">
              <span>
                {perceptionFile
                  ? perceptionFile.name
                  : "No file selected"}
              </span>

              <span className="bg-blue-600 text-white px-3 py-1 rounded">
                Choose File
              </span>

              <input
                type="file"
                accept=".csv"
                className="hidden"
                onChange={(e) =>
                  setPerceptionFile(e.target.files[0])
                }
              />
            </label>
          </div>
        </div>

        {/* Button */}
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
              <h3 className="text-gray-600">
                Total Claims
              </h3>
              <p className="text-2xl font-bold">
                {stats.total}
              </p>
            </div>

            <div className="bg-green-50 p-6 rounded-xl shadow">
              <h3 className="text-gray-600">
                Avg Disputability
              </h3>
              <p className="text-2xl font-bold">
                {stats.avgDisputability}
              </p>
            </div>

          </div>
        )}

           {/*Ci= i-th claim,
           Pi= Number of positive perception,
           Ni= Number of negative perception*/}
        {stats && (
           
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg mb-8">
            <h3 className="font-semibold text-lg mb-2">
              Disputability Formula
            </h3>

            <p className="text-gray-700">
              Disputability is calculated with the formula:
            </p>

            <p className="mt-2 font-mono text-blue-700">
              D(Ci) = |Pi-Ni|/(Pi+Ni)
            </p>
            <p classname="text-gray-700">Ci= i-th claim,  Pi= Number of positive perception, Ni= Number of negative perception </p>
          </div>
        )}

        {/* Tables */}
        {renderTable("False Claims (O1)", results.false_claims)}
        {renderTable(
          "Most Misperceived (O2)",
          results.most_misperceived_claims
        )}
        {renderTable(
          "Most Disputed (O3)",
          results.most_disputed_claims
        )}

      </div>
    </div>
  );
}

export default App;