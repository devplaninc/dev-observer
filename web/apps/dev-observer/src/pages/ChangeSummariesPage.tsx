import React from "react";
import {ChangeSummaryTimeline} from "@/components/analysis/ChangeSummaryTimeline.tsx";

const ChangeSummariesPage: React.FC = () => {
  // TODO: Implement data fetching for change summaries
  // For now, show empty state
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Change Summaries</h1>
      <ChangeSummaryTimeline />
    </div>
  );
};

export default ChangeSummariesPage; 