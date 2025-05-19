import { BrowserRouter, Routes, Route, Navigate } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import RepositoryListPage from './pages/RepositoryListPage';
import RepositoryDetailsPage from './pages/RepositoryDetailsPage';
import { ThemeToggle } from './components/ui/theme-toggle';

// Create a client
const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-background text-foreground">
          <div className="fixed top-4 right-4 z-50">
            <ThemeToggle />
          </div>
          <Routes>
            <Route path="/repositories" element={<RepositoryListPage />} />
            <Route path="/repositories/:id" element={<RepositoryDetailsPage />} />
            <Route path="/" element={<Navigate to="/repositories" replace />} />
            <Route path="*" element={<Navigate to="/repositories" replace />} />
          </Routes>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
