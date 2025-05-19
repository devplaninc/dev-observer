import {Alert, AlertDescription, AlertTitle} from "@/components/ui/alert";
import {AlertCircle} from "lucide-react";

export function ErrorAlert({err}: { err: Error | string }) {
  const message = err instanceof Error ? err.message : err
  const details = err instanceof Error && JSON.stringify(err, undefined, 2)
  return <Alert variant="destructive">
    <AlertCircle className="h-4 w-4"/>
    <AlertTitle>Error</AlertTitle>
    <AlertDescription>
      {message}
      {details && <pre className="text-sm">{details}</pre>}
    </AlertDescription>
  </Alert>
}