import React, { useState } from 'react';

const GPTConsole: React.FC = () => {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch(`${import.meta.env.VITE_API_URL}/api/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: input }),
    });
    const data = await res.json();
    setOutput(JSON.stringify(data, null, 2));
    setInput('');
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <input
        type="text"
        value={input}
        onChange={e => setInput(e.target.value)}
        className="bg-transparent border-b-2 border-accent text-accent text-lg focus:outline-none"
        placeholder="> Enter command"
      />
      {output && (
        <pre className="bg-black/40 p-3 rounded text-sm whitespace-pre-wrap text-white border border-accent/30">
          {output}
        </pre>
      )}
    </form>
  );
};

export default GPTConsole;
