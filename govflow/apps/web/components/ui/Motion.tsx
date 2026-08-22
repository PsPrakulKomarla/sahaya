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
      variants={variants}
      initial={initial}
      animate={animate}
      exit={exit}
      className={cn("relative", className)}
      {...props}
    />
  );
}

export function motionImg({
  src,
  alt,
  className,
  whileHover,
  whileTap,
  ...props
}: {
  src: string;
  alt: string;
  className?: string;
  whileHover?: Record<string, any>;
  whileTap?: Record<string, any>;
  [key: string]: any;
}) {
  return (
    <motion.img
      src={src}
      alt={alt}
      className={cn("block transition-colors", className)}
      whileHover={whileHover}
      whileTap={whileTap}
      {...props}
    />
  );
}

export function motionButton({
  children,
  className,
  whileHover,
  whileTap,
  variants,
  initial = "hidden",
  animate = "visible",
  exit = "hidden",
  ...props
}: {
  children: React.ReactNode;
  className?: string;
  whileHover?: Record<string, any>;
  whileTap?: Record<string, any>;
  variants?: Record<string, Record<string, any>>;
  initial?: string | Record<string, any>;
  animate?: string | Record<string, any>;
  exit?: string | Record<string, any>;
  [key: string]: any;
}) {
  return (
    <motion.button
      variants={{ variants, initial, animate, exit }}
      className={cn(
        "inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium transition-all",
        "focus:outline-none focus:ring-2 focus:ring-offset-2",
        whileHover && "hover:scale-105",
        whileTap && "active:scale-95",
        className
      )}
      whileHover={whileHover}
      whileTap={whileTap}
      {...props}
    >
      {children}
    </motion.button>
  );
}

export function motionCard({
  className,
  whileHover,
  whileTap,
  variants,
  initial = "hidden",
  animate = "visible",
  ...props
}: {
  className?: string;
  whileHover?: Record<string, any>;
  whileTap?: Record<string, any>;
  variants?: Record<string, Record<string, any>>;
  initial?: string | Record<string, any>;
  animate?: string | Record<string, any>;
  exit?: string | Record<string, any>;
  [key: string]: any;
}) {
  return (
    <motion.div
      variants={{ variants, initial, animate, exit }}
      className={cn(
        "bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm transition-all duration-300 hover:scale-[1.02]",
        whileHover && "hover:shadow-lg",
        whileTap && "active:scale-[0.98]",
        className
      )}
      {...props}
    />
  );
}

export function motionListItem({
  itemVariant,
  index,
  className,
  ...props
}: {
  itemVariant?: string;
  index: number;
  className?: string;
  [key: string]: any;
}) {
  const staggerChildren = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 20,
      },
    },
  };

  return (
    <motion.li
      className={cn(
        "flex items-center gap-4 rounded-lg px-4 py-3 transition-all",
        "data-[state=active]:bg-primary-50 dark:data-[state=active]:bg-primary-500/20",
        className
      )}
      ...props
    />
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

export useMotionTap {
  const onTap = (event: React.GestureEvent) => {
    // Handle tap gestures
  };

  return { onTap };
}