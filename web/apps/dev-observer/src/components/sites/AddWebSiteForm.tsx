import React, {useState} from "react";
import {zodResolver} from "@hookform/resolvers/zod";
import {useForm} from "react-hook-form";
import * as z from "zod";
import {Button} from "@/components/ui/button.tsx";
import {Form, FormControl, FormField, FormItem, FormMessage} from "@/components/ui/form.tsx";
import {Input} from "@/components/ui/input.tsx";
import {toast} from "sonner";
import {useBoundStore} from "@/store/use-bound-store.tsx";

const formSchema = z.object({
  url: z.string().url("Please enter a valid URL"),
});

type FormValues = z.infer<typeof formSchema>;

const AddWebSiteForm: React.FC = () => {
  const {addWebSite} = useBoundStore()
  const [adding, setAdding] = useState(false);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      url: "",
    },
  });

  const onSubmit = async (values: FormValues) => {
    setAdding(true);
    await addWebSite(values.url)
      .catch(error => toast.error(`Failed to add website: ${error}`))
      .then(() => {
        form.reset();
        toast.success("Website added successfully");
      })
      .finally(() => setAdding(false));
  }

  return (
    <Form {...form}>
      {/* eslint-disable-next-line @typescript-eslint/no-misused-promises */}
      <form onSubmit={form.handleSubmit(onSubmit)} className="flex space-x-2">
        <FormField
          control={form.control}
          name="url"
          render={({field}) => (
            <FormItem className="flex-1">
              <FormControl>
                <Input
                  placeholder="Enter website URL (e.g., https://example.com)"
                  {...field}
                  disabled={adding}
                />
              </FormControl>
              <FormMessage/>
            </FormItem>
          )}
        />
        <Button type="submit" disabled={adding}>
          {adding ? "Adding..." : "Add Website"}
        </Button>
      </form>
    </Form>
  );
};

export default AddWebSiteForm;