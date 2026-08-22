import { cn } from "@/lib/utils";

export function ResponsiveWrapper({
  children,
  className,
  ...props
}: {
  children: React.ReactNode;
  className?: string;
  [key: string]: any;
}) {
  return (
    <div
      className={cn(
        "max-w-6xl mx-auto px-4 sm:px-6 lg:px-8",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function useResponsiveBreakpoint({
  breakpoint = "sm",
}: {
  breakpoint?: "sm" | "md" | "lg" | "xl";
}) {
  const [isAbove, setIsAbove] = React.useState(false);

  React.useEffect(() => {
    const handleResize = () => {
      const breakpoints = {
        sm: 640,
        md: 768,
        lg: 1024,
        xl: 1280,
      };
      const width = typeof window !== "undefined" ? window.innerWidth : 0;
      setIsAbove(width > breakpoints[breakpoint]);
    };

    handleResize();
    window.addEventListener("resize", handleResize);

    return () => window.removeEventListener("resize", handleResize);
  }, [breakpoint]);

  return isAbove;
}

export function useMobileBackButton({
  onBack,
}: {
  onBack: () => void;
}) {
  React.useEffect(() => {
    const handleBack = (event:PopStateEvent) => {
      event.preventDefault();
      onBack();
    };

    const listener = (event: PopStateEvent) => {
      onBack();
    };

    window.addEventListener("popstate", listener);

    return () => {
      window.removeEventListener("popstate", listener);
    };
  }, [onBack]);
}

export function MobileNavLink({
  href,
  children,
  className,
  ...props
}: {
  href: string;
  children: React.ReactNode;
  className?: string;
  [key: string]: any;
}) {
  return (
    <a
      href={href}
      className={cn(
        "block rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:text-slate-900 dark:text-slate-300 dark:hover:text-slate-100",
        "data-[state=active]:bg-primary-100 dark:data-[state=active]:bg-primary-900/20",
        className
      )}
      {...props}
    >
      {children}
    </a>
  );
}

export function MobileSafeArea({
  children,
  className,
  ...props
}: {
  children: React.ReactNode;
  className?: string;
  [key: string]: any;
}) {
  return (
    <div
      className={cn(
        "min-h-screen bg-slate-50 dark:bg-slate-900",
        "pb-24 md:pb-32 lg:pb-40",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function ResponsiveGrid({
  children,
  mobileClass,
  tabletClass,
  desktopClass,
  ...props
}: {
  children: React.ReactNode;
  mobileClass: string;
  tabletClass: string;
  desktopClass: string;
  className?: string;
  [key: string]: any;
}) {
  return (
    <div
      className={cn(
        "grid grid-cols-1 gap-4",
        `sm:grid-cols-${mobileClass.replace("col-", "")}`,
        `md:grid-cols-${tabletClass.replace("col-", "")}`,
        `lg:grid-cols-${desktopClass.replace("col-", "")}`,
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function ResponsiveText({
  base,
  sm,
  md,
  lg,
  xl,
  className,
  ...props
}: {
  base: string;
  sm?: string;
  md?: string;
  lg?: string;
  xl?: string;
  className?: string;
  [key: string]: any;
}) {
  const sizes = {
    base,
    sm: sm || base,
    md: md || base,
    lg: lg || base,
    xl: xl || base,
  };

  return (
    <p
      className={cn(
        "text-[${sizes.base}]",
        `sm:text-[${sizes.sm}]`,
        `md:text-[${sizes.md}]`,
        `lg:text-[${sizes.lg}]`,
        `xl:text-[${sizes.xl}]`,
        className
      )}
      {...props}
    />
  );
}

export function useScrollLock({
  enable = true,
}: {
  enable?: boolean;
}) {
  React.useEffect(() => {
    if (!enable) return;

    const originalOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = "hidden";

    return () => {
      document.documentElement.style.overflow = originalOverflow;
    };
  }, [enable]);
}