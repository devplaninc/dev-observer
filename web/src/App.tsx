import {BrowserRouter, Navigate, Route, Routes} from 'react-router';
import {QueryClient, QueryClientProvider} from '@tanstack/react-query';
import RepositoryListPage from './pages/RepositoryListPage';
import RepositoryDetailsPage from './pages/RepositoryDetailsPage';
import GlobalConfigEditorPage from "@/pages/config/GlobalConfigEditorPage.tsx";
import {SidebarInset, SidebarProvider} from "@/components/ui/sidebar.tsx";
import {SiteHeader} from "@/components/layout/SiteHeader.tsx";
import {AppSidebar} from "@/components/layout/AppSidebar.tsx";

// Create a client
const queryClient = new QueryClient();

function App() {
  return <div className="[--header-height:calc(theme(spacing.14))]">
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <SidebarProvider className="flex flex-col">
        <div className="min-h-screen bg-background text-foreground">
          <SiteHeader />
          <div className="flex flex-1">
            <AppSidebar />
            <SidebarInset>
              <Routes>
                <Route path="/repositories" element={<RepositoryListPage />} />
                <Route path="/repositories/:id" element={<RepositoryDetailsPage />} />
                <Route path="/admin/config-editor" element={<GlobalConfigEditorPage />} />
                <Route path="/" element={<Navigate to="/repositories" replace />} />
                <Route path="*" element={<Navigate to="/repositories" replace />} />
              </Routes>
            </SidebarInset>
          </div>
        </div>
        </SidebarProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </div>;
}

export default App;
