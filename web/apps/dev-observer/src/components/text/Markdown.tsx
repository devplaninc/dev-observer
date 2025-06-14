import {type FC, memo} from "react";
import ReactMarkdown, {type Options} from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";

const MemoizedReactMarkdown: FC<Options> = memo(
  ReactMarkdown,
  (prevProps, nextProps) => prevProps.children === nextProps.children,
);

export const Markdown = ({content}: { content: string }) => {
  return <div className="prose prose-sm w-full text-sm max-w-full">
    <MemoizedReactMarkdown remarkPlugins={[remarkGfm, remarkMath]}>
      {content}
    </MemoizedReactMarkdown>
  </div>
};