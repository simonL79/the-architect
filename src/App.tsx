import React from 'react';
import ArchitectLayout from './components/ArchitectLayout';
import GPTConsole from './components/GPTConsole';

const App: React.FC = () => {
  return (
    <ArchitectLayout>
      <GPTConsole />
    </ArchitectLayout>
  );
};

export default App;
