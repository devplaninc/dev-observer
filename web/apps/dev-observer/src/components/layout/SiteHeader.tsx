import {useSidebar} from "../ui/sidebar.tsx"
import {Button} from "@/components/ui/button.tsx";
import {SidebarIcon} from "lucide-react";
import {ThemeToggle} from "@/components/ui/theme-toggle.tsx";

export function SiteHeader() {
  const { toggleSidebar } = useSidebar()
  return (
    <header className="flex sticky top-0 z-50 w-full items-center border-b bg-background">
      <div className="flex h-[--header-height] w-full items-center px-4 justify-between">
        <div className="flex items-center gap-2 py-3">
          <Button
            className="size-8"
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
          >
            <SidebarIcon />
          </Button>
        </div>
        <div className="flex items-center gap-2">
          {/*<SearchForm className="sm:ml-auto sm:w-auto" />*/}
          <ThemeToggle />
        </div>
      </div>
    </header>
  )
}