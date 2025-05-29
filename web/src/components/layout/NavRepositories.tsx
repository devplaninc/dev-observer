import {type LucideIcon, MoreHorizontal,} from "lucide-react"
import {useMemo, useState} from "react";
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar.tsx"

export function NavRepositories({
                                  repositories,
                                }: {
  repositories: {
    name: string
    url: string
    icon?: LucideIcon
  }[]
}) {
  // const { isMobile } = useSidebar()
  const toShowCnt = 4
  const [showAll, setShowAll] = useState(repositories.length <= toShowCnt)
  const shown = useMemo(
    () => showAll ? repositories : repositories.slice(0, toShowCnt), [repositories, showAll])

  return (
    <SidebarGroup className="group-data-[collapsible=icon]:hidden">
      <SidebarGroupLabel>Projects</SidebarGroupLabel>
      <SidebarMenu>
        {shown.map((item) => (
          <SidebarMenuItem key={item.name}>
            <SidebarMenuButton asChild>
              <a href={item.url}>
                {item.icon && <item.icon/>}
                <span>{item.name}</span>
              </a>
            </SidebarMenuButton>
            {/*<DropdownMenu>*/}
            {/*  <DropdownMenuTrigger asChild>*/}
            {/*    <SidebarMenuAction showOnHover>*/}
            {/*      <MoreHorizontal />*/}
            {/*      <span className="sr-only">More</span>*/}
            {/*    </SidebarMenuAction>*/}
            {/*  </DropdownMenuTrigger>*/}
            {/*  <DropdownMenuContent*/}
            {/*    className="w-48"*/}
            {/*    side={isMobile ? "bottom" : "right"}*/}
            {/*    align={isMobile ? "end" : "start"}*/}
            {/*  >*/}
            {/*    <DropdownMenuItem>*/}
            {/*      <Folder className="text-muted-foreground" />*/}
            {/*      <span>View Project</span>*/}
            {/*    </DropdownMenuItem>*/}
            {/*    <DropdownMenuItem>*/}
            {/*      <Share className="text-muted-foreground" />*/}
            {/*      <span>Share Project</span>*/}
            {/*    </DropdownMenuItem>*/}
            {/*    <DropdownMenuSeparator />*/}
            {/*    <DropdownMenuItem>*/}
            {/*      <Trash2 className="text-muted-foreground" />*/}
            {/*      <span>Delete Project</span>*/}
            {/*    </DropdownMenuItem>*/}
            {/*  </DropdownMenuContent>*/}
            {/*</DropdownMenu>*/}
          </SidebarMenuItem>
        ))}
        {!showAll && <SidebarMenuItem>
            <SidebarMenuButton onClick={() => setShowAll(true)}>
                <MoreHorizontal/>
                <span>More</span>
            </SidebarMenuButton>
        </SidebarMenuItem>}
      </SidebarMenu>
    </SidebarGroup>
  )
}
