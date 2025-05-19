import {Loader2} from "lucide-react";
import {cn} from "@/lib/utils";
import {type CSSProperties, type FC, memo} from "react";

export const Loader: FC<{ className?: string, style?: CSSProperties }> = memo(
  LoaderComponent,
  (prevProps, nextProps) => prevProps.className == nextProps.className && prevProps.style == nextProps.style
)

function LoaderComponent({className, style}: { className?: string, style?: CSSProperties }) {
  return <Loader2 className={cn("animate-spin", className)} style={style}/>
}