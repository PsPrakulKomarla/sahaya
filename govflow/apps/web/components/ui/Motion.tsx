import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export function motionDiv({
  variants,
  initial,
  animate,
  exit,
  className,
  ...props
}: {
  variants?: Record<string, Record<string, any>>;
  initial?: string | Record<string, any>;
  animate?: string | Record<string, any>;
  exit?: string | Record<string, any>;
  className?: string;
  [key: string]: any;
}) {
  return (
    <motion.div
      className={cn(
        "flex flex-col items-center py-8",
        className
      )}
      {...props}
    >
      <h2 className="text-2xl font-bold mb-4">Motion Component</h2>
    </motion.div>
  );
}

export function motionHeader({
  className,
  ...props
}: {
  className?: string;
  [key: string]: any;
}) {
  return (
    <motion.header
      className={cn(
        "bg-white dark:bg-slate-900 border-b border-slate-200/50 transition-colors",
        "data-[state=hover]:bg-slate-50 dark:data-[state=hover]:bg-slate-950",
        className
      )}
      {...props}
    />
  );
}

export function useMotionTap({
  className,
  ...props
}: {
  className?: string;
  [key: string]: any;
}) {
  const onTap = (event: React.GestureEvent) => {
    // Handle tap gestures
  };

  return { onTap };
}