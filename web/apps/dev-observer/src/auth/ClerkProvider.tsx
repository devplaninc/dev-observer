import React from 'react';
import {ClerkProvider as ClerkProviderOriginal, SignedIn, SignedOut, SignIn} from '@clerk/clerk-react';
import {dark} from '@clerk/themes';
import {useTheme} from '@/components/ui/theme-provider.tsx';
import {useBoundStore} from "@/store/use-bound-store.tsx";
import {useShallow} from "zustand/react/shallow";

interface ClerkProviderProps {
  children: React.ReactNode;
}

export function ClerkProvider({ children }: ClerkProviderProps) {
  const usersStatus = useBoundStore(useShallow(s => s.usersStatus))
  const { theme } = useTheme();

  // If user management is disabled, render children directly
  if (!usersStatus?.enabled) {
    return <>{children}</>;
  }

  // If user management is enabled but no frontend API key is provided, show error
  if (!usersStatus?.publicApiKey) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4">
        <h1 className="text-2xl font-bold text-red-500 mb-4">Configuration Error</h1>
        <p className="text-center">
          User management is enabled but no Clerk frontend API key is configured.
          Please contact the administrator.
        </p>
      </div>
    );
  }

  // If user management is enabled and frontend API key is provided, wrap with ClerkProvider
  return (
    <ClerkProviderOriginal 
      publishableKey={usersStatus?.publicApiKey}
      appearance={{
        baseTheme: theme === 'dark' ? dark : undefined,
        elements: {
          formButtonPrimary: 'bg-primary hover:bg-primary/90',
          card: 'bg-background border border-border shadow-sm',
          headerTitle: 'text-foreground',
          headerSubtitle: 'text-muted-foreground',
          formFieldLabel: 'text-foreground',
          formFieldInput: 'bg-input border-input text-foreground',
          footerActionLink: 'text-primary hover:text-primary/90',
        }
      }}
    >
      <SignedIn>
        {children}
      </SignedIn>
      <SignedOut>
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-full max-w-md">
            <SignIn />
          </div>
        </div>
      </SignedOut>
    </ClerkProviderOriginal>
  );
}