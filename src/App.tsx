import React from 'react';
import GPTConsole from './components/GPTConsole';
import ArchitectLayout from './components/ArchitectLayout';

const App: React.FC = () => {
  return (
    <ArchitectLayout>
      <GPTConsole />
    </ArchitectLayout>
  );
};

export default App;

