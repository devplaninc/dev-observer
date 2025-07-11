import {Checkbox} from "@/components/ui/checkbox.tsx";

interface EnrollmentToggleProps {
  repoId: string;
  repoName: string;
  isEnrolled: boolean;
  onToggle: (enrolled: boolean) => void;
  isLoading?: boolean;
}

export function EnrollmentToggle({isEnrolled, onToggle, isLoading = false}: EnrollmentToggleProps) {
  const handleToggle = () => {
    onToggle(!isEnrolled);
  };

  return (
    <div className="flex items-center space-x-2">
      <Checkbox
        checked={isEnrolled}
        onCheckedChange={handleToggle}
        disabled={isLoading}
      />
      <span className="text-sm text-muted-foreground">
        {isEnrolled ? "Enrolled" : "Not enrolled"} for change analysis
      </span>
    </div>
  );
} 