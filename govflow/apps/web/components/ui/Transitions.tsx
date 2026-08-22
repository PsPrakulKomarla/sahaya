import { motion } from "framer-motion";
import { useLocation } from "next/navigation";
import { useEffect } from "react";

export function PageTransition({
  children,
  className,
  ...props
}: {
  children: React.ReactNode;
  className?: string;
  [key: string]: any;
}) {
  const location = useLocation();

  useEffect(() => {
    // Trigger page transition on location change
    const startProgress = document.querySelector(
      '.page-progress-bar'
    ) as HTMLDivElement | null;

    if (startProgress) {
      startProgress.style.transition = "width 0.3s ease";
      startProgress.style.width = "100%";

      setTimeout(() => {
        startProgress.style.width = "0%";
      }, 300);
    }
  }, [location]);

  return (
    <div
      className={cn(
        "fixed inset-0 pointer-events-none z-40",
        className
      )}
      {...props}
    >
      <motion.div
        className="absolute top-0 left-0 right-0 h-0.5 bg-primary-600 dark:bg-primary-700 transition-all"
        animate={{ width: "100%" }}
        exit={{ width: "0%" }}
        transition={{ duration: 0.3, delay: 0.1 }}
      />
      <motion.div
        className="absolute top-0 left-0 right-0 h-full bg-black/50 transition-all"
        animate={{ opacity: 0 }}
        exit={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      />
    </div>
  );
}

export function motionImage({
  src,
  alt,
  className,
  whileInView,
  ...props
}: {
  src: string;
  alt: string;
  className?: string;
  whileInView?: Record<string, any>;
  [key: string]: any;
}) {
  return (
    <motion.img
      src={src}
      alt={alt}
      className={cn("lazy-load transition-opacity", className)}
      whileInView={whileInView}
      transition={{ duration: 0.5 }}
      {...props}
    />
  );
}

export function motionReveal({
  direction = "up",
  className,
  ...props
}: {
  direction?: "up" | "down" | "left" | "right";
  className?: string;
  [key: string]: any;
}) {
  const directionMap = {
    up: { initial: { y: 20, opacity: 0 }, animate: { y: 0, opacity: 1 } },
    down: { initial: { y: -20, opacity: 0 }, animate: { y: 0, opacity: 1 } },
    left: { initial: { x: -20, opacity: 0 }, animate: { x: 0, opacity: 1 } },
    right: { initial: { x: 20, opacity: 0 }, animate: { x: 0, opacity: 1 } },
  };

  const config = directionMap[direction];

  return (
    <motion.div
      initial={config.initial}
      animate={config.animate}
      className={cn(
        "reveal transition-all duration-500 ease-out",
        className
      )}
      {...props}
    />
  );
}