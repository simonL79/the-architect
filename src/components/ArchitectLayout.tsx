import React from 'react';

const ArchitectLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-background text-white p-6 grid grid-cols-4 gap-4">
      {/* Console Panel */}
      <div className="col-span-2 bg-panel rounded-lg p-4 flex flex-col gap-4 shadow-xl">
        <h1 className="text-2xl text-accent font-bold tracking-wider">
          🧠 The Architect Console
        </h1>
        {children}
      </div>

      {/* Display Panels */}
      <div className="col-span-2 grid grid-rows-2 gap-4">
        <div className="bg-panel rounded-lg p-4 shadow-md">📡 System Status</div>
        <div className="bg-panel rounded-lg p-4 shadow-md">🧾 Memory / Log</div>
      </div>
    </div>
  );
};

export default ArchitectLayout;
