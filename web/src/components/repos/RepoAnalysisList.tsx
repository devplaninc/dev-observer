import type {GitHubRepository} from "@/pb/dev_observer/api/types/repo.ts";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import {useShallow} from "zustand/react/shallow";
import {Loader} from "@/components/Loader.tsx";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Accordion, AccordionContent, AccordionItem, AccordionTrigger} from "@/components/ui/accordion.tsx";
import {Markdown} from "@/components/text/Markdown.tsx";
import type {ObservationKey} from "@/pb/dev_observer/api/types/observations.ts";
import {useObservation} from "@/hooks/useObservationQueries.ts";
import {ErrorAlert} from "@/components/ErrorAlert.tsx";

export function RepoAnalysisList({repo}: { repo: GitHubRepository }) {
  const keys = useBoundStore(useShallow(s => {
    console.log("observationKeys", {observationKeys: s.observationKeys})
    return s.observationKeys.repos?.filter(k => k.key.startsWith(repo.fullName))
  }))
  console.log("KEYS", {keys})
  if (keys === undefined) {
    return <Loader/>
  }
  if (keys.length === 0) {
    return <Card>
      <CardHeader>
        <CardTitle>Analysis Data</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="bg-muted p-8 rounded-lg text-center">
          <h3 className="text-xl font-medium mb-2">No analysis data available</h3>
        </div>
      </CardContent>
    </Card>
  }
  return <div className="space-y-4">
    <div className="font-semibold">
      Analysis Data
    </div>
    <div>
      <Accordion type="multiple" className="w-full">
        {keys.map(key => <AccordionItem value={key.name} key={key.key}>
          <AccordionTrigger className="text-sm font-medium justify-start">
            {key.name}
          </AccordionTrigger>

          <AccordionContent className="pl-4">
            <AnalysisContent observationKey={key}/>
          </AccordionContent>
        </AccordionItem>)}

      </Accordion>
    </div>
  </div>
}

function AnalysisContent({observationKey}: { observationKey: ObservationKey }) {
  const {observation, error} = useObservation(observationKey)
  if (!observation) {
    if (error) {
      return <ErrorAlert err={error}/>
    }
    return <Loader/>
  }
  return <Markdown content={observation.content}/>
}