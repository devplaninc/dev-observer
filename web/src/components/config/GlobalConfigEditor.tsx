import {useFieldArray, useForm} from "react-hook-form";
import {z} from "zod";
import {zodResolver} from "@hookform/resolvers/zod";
import {GlobalConfig} from "@/pb/dev_observer/api/types/config.ts";
import {useCallback} from "react";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import {toast} from "sonner";
import {Form, FormControl, FormField, FormItem, FormLabel, FormMessage} from "@/components/ui/form.tsx";
import {Input} from "@/components/ui/input.tsx";
import {Button} from "@/components/ui/button.tsx";
import {Analyzer} from "@/pb/dev_observer/api/types/observations.ts";
import {useGlobalConfig} from "@/hooks/use-config.tsx";
import {ErrorAlert} from "@/components/ErrorAlert.tsx";
import {Loader} from "@/components/Loader.tsx";

const analyzerSchema = z.object({
  name: z.string().min(2),
  promptPrefix: z.string().min(2),
  fileName: z.string().min(2),
})

const analysisConfigSchema = z.object({
  repoAnalyzers: z.array(analyzerSchema),
})

const globalConfigSchema = z.object({
  analysis: analysisConfigSchema,
})

export type globalConfigType = z.infer<typeof globalConfigSchema>

export function GlobalConfigEditor() {
  const {config, error} = useGlobalConfig()
  if (!config) {
    if (error) {
      return <ErrorAlert err={error}/>
    }
    return <Loader/>
  }
  return <GlobalConfigEditorForm config={config}/>
}

function GlobalConfigEditorForm({config}: { config: GlobalConfig }) {
  const {updateGlobalConfig} = useBoundStore()
  const form = useForm<globalConfigType>({
    resolver: zodResolver(globalConfigSchema),
    defaultValues: config,
  });
  const onSubmit = useCallback((values: globalConfigType) => {
      updateGlobalConfig(values)
        .then(() => toast.success("Profile updated"))
        .catch(e => {
          toast.error(`Failed to update profile: ${e}`)
          throw e
        })
    }
    , [updateGlobalConfig])
  const {fields: analyzers, remove, append} = useFieldArray({name: "analysis.repoAnalyzers", control: form.control});
  return <Form {...form}>
    {/* eslint-disable-next-line @typescript-eslint/no-misused-promises */}
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
      <div>
        <h2 className="font-semibold text-lg">Analyzers:</h2>
        {analyzers.map((f, i) => (
          <div key={f.id} className="border rounded-md p-4 w-11/12 space-y-4">
            <FormField
              control={form.control}
              name={`analysis.repoAnalyzers.${i}.name`}
              render={({field}) => (
                <FormItem className="flex items-center gap-4">
                  <FormLabel className="w-[100px]">Name:</FormLabel>
                  <FormControl className="w-[200px]">
                    <Input placeholder="Analyzer name" {...field}/>
                  </FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name={`analysis.repoAnalyzers.${i}.promptPrefix`}
              render={({field}) => (
                <FormItem className="flex items-center gap-4">
                  <FormLabel className="w-[100px]">Prompt PRefix:</FormLabel>
                  <FormControl className="w-[200px]">
                    <Input placeholder="Analyzer prompt prefix" {...field}/>
                  </FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name={`analysis.repoAnalyzers.${i}.fileName`}
              render={({field}) => (
                <FormItem className="flex items-center gap-4">
                  <FormLabel className="w-[100px]">File Name:</FormLabel>
                  <FormControl className="w-[200px]">
                    <Input placeholder="Analyzer file name" {...field}/>
                  </FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />

            <Button onClick={() => remove(i)}>Remove</Button>
          </div>
        ))}
        <Button onClick={(e) => {
          e.preventDefault()
          append(Analyzer.create({name: '', promptPrefix: '', fileName: "analysis.md"}))
        }
        }>
          Add Analyzer
        </Button>
      </div>

      <Button role="submit">
        Submit
      </Button>
    </form>
  </Form>
}