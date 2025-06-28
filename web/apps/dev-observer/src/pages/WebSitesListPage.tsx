import React from "react";
import AddWebSiteForm from "@/components/sites/AddWebSiteForm.tsx";
import WebSitesList from "@/components/sites/WebSitesList.tsx";

const WebSitesListPage: React.FC = () => {
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Websites</h1>

      <div>
        <AddWebSiteForm />
      </div>

      <WebSitesList />
    </div>
  );
};

export default WebSitesListPage;