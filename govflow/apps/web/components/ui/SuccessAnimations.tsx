import { CheckCircle, Star, Sparkles } from "lucide-react";

export function SuccessCheckmark({
  size = 64,
  color = "bg-green-500 dark:bg-green-900/30",
  className,
  ...props
}: {
  size?: number;
  color?: string;
  className?: string;
  ...props
}) {
  return (
    <div
      className={cn(
        "relative w-full h-full",
        className
      )}
      {...props}
    >
      <svg
        className={cn(
          "absolute inset-0 w-full h-full",
          color,
          "rounded-full"
        )}
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={size / 2 - 4}
          fill="none"
          stroke="currentColor"
          strokeWidth={4}
        />
        <path
          fill="white"
          d="M2 12l3.09 5.79 15.91-15.91L2 12Z"
        />
      </svg>

      <CheckCircle
        className={cn(
          "relative z-10 text-white",
          "h-",
        )}
        size={size}
      />
    </div>
  );
}

export function SuccessConfetti({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "pointer-events-none absolute bottom-0 left-0 w-full h-1 bg-primary-600 dark:bg-primary-500 overflow-hidden rounded-t-lg",
        className
      )}
      {...props}
    >
      <div
        className="h-full absolute top-0 w-1/4 bg-primary-600 dark:bg-primary-500 opacity-100"
        style={{ animation: `confetti-1 3s ease-out forwards` }}
      />
      <div
        className="h-full absolute top-0 w-1/4 bg-primary-600 dark:bg-primary-500 opacity-100"
        style={{ animation: `confetti-2 3s ease-out forwards` }}
      />
      <div
        className="h-full absolute top-0 w-1/4 bg-primary-600 dark:bg-primary-500 opacity-100"
        style={{ animation: `confetti-3 3s ease-out forwards` }}
      />
      <div
        className="h-full absolute top-0 w-1/4 bg-primary-600 dark:bg-primary-500 opacity-100"
        style={{ animation: `confetti-4 3s ease-out forwards` }}
      />
    </div>
  );
}

export function SuccessToast({
  title = "Success!",
  description = "Your request has been completed successfully.",
  variant = "default",
  ...props
}: {
  title?: string;
  description?: string;
  variant?: "default" | "gov" | "success";
  className?: string;
  ...props
}) {
  const variantStyles = {
    default: "bg-white dark:bg-slate-800",
    gov: "bg-white dark:bg-slate-800 border-l-4 border-gov-blue",
    success: "bg-green-100 dark:bg-green-900/30 border-l-4 border-green-500",
  };

  return (
    <div
      className={cn(
        "fixed bottom-4 right-4 z-50 rounded-lg shadow-2xl max-w-xs w-full transform translate-y-6 transition-all duration-500 ease-out",
        variantStyles[variant],
        className
      )}
      {...props}
    >
      <div className="flex items-start gap-4 p-5">

        <div className="flex-shrink-0 pt-1">
          {variant === "gov" && (
            <svg
              className={cn("h-6 w-6 text-gov-blue", "opacity-80")}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M22 11.08V12a10 10 0 1 1-5.94-9.14" />
              <polyline points="22 4 12 15 2 4" />
            </svg>
          )}
          {variant === "success" && (
            <svg
              className={cn("h-6 w-6 text-green-600", "opacity-80")}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
          )}
          {variant === "default" && (
            <svg
              className={cn("h-6 w-6 text-primary-600", "opacity-80")}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
          )}
        </div>

        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-medium text-slate-900 dark:text-white">
            {title}
          </h3>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            {description}
          </p>
        </div>
      </div>
    </div>
  );
}

export function useSuccessToast() {
  const [isVisible, setIsVisible] = React.useState(false);

  const show = React.useCallback(
    (options: {
      title?: string;
      description?: string;
      variant?: "default" | "gov" | "success";
      duration?: number;
    }) => {
      setIsVisible(true);
      const { duration = 4000, ...rest } = options;
      const toast = document.querySelector(".govflow-toast") as HTMLElement | null;
      if (toast) {
        toast.style.transitionDuration = `${duration}ms`;
      }
      setTimeout(() => setIsVisible(false), duration);
    },
    []
  );

  return { isVisible, show };
}