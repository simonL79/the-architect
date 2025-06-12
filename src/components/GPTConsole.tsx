import React, { useState } from "react";

const GPTConsole: React.FC = () => {
  const [command, setCommand] = useState("");
  const [output, setOutput] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const API = import.meta.env.VITE_API_URL;

  const runCommand = async () => {
    if (!command.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command }),
      });
      const data = await res.json();
      setOutput(JSON.stringify(data, null, 2));
    } catch (err) {
      setOutput("Error reaching backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 bg-gray-900 text-white rounded-lg">
      <h2 className="text-lg font-bold mb-2">GPT Command Console</h2>
      <div className="flex gap-2 mb-2">
        <input
          type="text"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          className="flex-1 p-2 text-black rounded"
          placeholder="Enter command (e.g. status check)"
        />
        <button
          onClick={runCommand}
          className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
        >
          {loading ? "Running..." : "Run"}
        </button>
      </div>
      {output && (
        <pre className="bg-black text-green-400 p-3 rounded text-sm max-h-60 overflow-y-auto">
          {output}
        </pre>
      )}
    </div>
  );
};

export default GPTConsole;