import * as React from "react"
import {useMemo} from "react"
import {ShieldUser, SquareTerminal,} from "lucide-react"

import {NavSecondary} from "@/components/nav-secondary"
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import {NavMain} from "@/components/layout/NavMain.tsx";
import {NavRepositories} from "@/components/layout/NavRepositories.tsx";
import {useRepositories} from "@/hooks/useRepositoryQueries.ts";
import {ErrorAlert} from "@/components/ErrorAlert.tsx";
import {Loader} from "@/components/Loader.tsx";

const data = {
  user: {
    name: "shadcn",
    email: "m@example.com",
    avatar: "/avatars/shadcn.jpg",
  },
  navMain: [
    {
      title: "Repositories",
      url: "/repositories",
      icon: SquareTerminal,
      isActive: true,
    },
    {
      title: "Admin",
      url: "",
      icon: ShieldUser,
      items: [
        {
          title: "Config",
          url: "/admin/config-editor",
        },
      ],
    },
  ],
  navSecondary: [
    // {
    //   title: "Support",
    //   url: "#",
    //   icon: LifeBuoy,
    // },
    // {
    //   title: "Feedback",
    //   url: "#",
    //   icon: Send,
    // },
  ],
}

export function AppSidebar({...props}: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar
      className="top-(--header-height) h-[calc(100svh-var(--header-height))]!"
      {...props}
    >
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <a href="/">
                {/*<div className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg">*/}
                {/*  <Command className="size-4" />*/}
                {/*</div>*/}
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-medium">Dev Observer</span>
                  {/*<span className="truncate text-xs">Enterprise</span>*/}
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain}/>
        <SidebarRepositories/>
        <NavSecondary items={data.navSecondary} className="mt-auto"/>
      </SidebarContent>
    </Sidebar>
  )
}

function SidebarRepositories() {
  const {repositories, error} = useRepositories()
  const reps = useMemo(
    () => repositories?.map(r => ({name: r.name, url: `/repositories/${r.id}`})) ?? [],
    [repositories])
  if (!repositories) {
    if (error) {
      return <ErrorAlert err={error}/>
    }
    return <Loader/>
  }
  return <NavRepositories repositories={reps}/>
}
