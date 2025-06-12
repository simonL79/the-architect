// Forced change to trigger clean rebuild
import React, { useState } from 'react';

const GPTConsole: React.FC = () => {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!input.trim()) return;

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: input }),
      });

      const data = await res.json();
      setOutput(JSON.stringify(data, null, 2));
    } catch (err) {
      setOutput(`Request failed: ${err}`);
    }

    setInput('');
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="> Enter command"
        className="bg-black border-b-2 border-accent text-accent p-2 text-lg focus:outline-none"
      />
      {output && (
        <pre className="bg-black/50 p-4 rounded text-sm text-white whitespace-pre-wrap">
          {output}
        </pre>
      )}
    </form>
  );
};

export default GPTConsole;

// ⬇ final build unlock

// Force new SHA for Vercel rebuild