import React from "react";
import { useParams } from "react-router";
import WebSiteDetails from "@/components/sites/WebSiteDetails.tsx";

const WebSiteDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6">Website Details</h1>
      {id ? <WebSiteDetails websiteId={id} /> : (
        <div className="bg-muted p-8 rounded-lg text-center">
          <h3 className="text-xl font-medium mb-2">Website ID not provided</h3>
          <p className="text-muted-foreground">
            Please select a website from the websites list.
          </p>
        </div>
      )}
    </div>
  );
};

export default WebSiteDetailsPage;