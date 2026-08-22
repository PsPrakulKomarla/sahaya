import { cn } from "@/lib/utils";

export function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-lg bg-slate-200 dark:bg-slate-700",
        "h-8 w-full shadow-sm",
        className
      )}
      {...props}
    />
  );
}

export function SkeletonCard({
  className,
  ...props
}: {
  className?: string;
}) {
  return (
    <div
      className={cn(
        "bg-slate-100 dark:bg-slate-800 rounded-xl p-6 animate-pulse",
        className
      )}
      {...props}
    />
  );
}

export function SkeletonAvatar({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "h-12 w-12 rounded-full bg-slate-200 dark:bg-slate-700 animate-pulse",
        className
      )}
      {...props}
    />
  );
}

export function SkeletonImage({
  className,
  ...props
}: React.HTMLAttributes<HTMLImageElement>) {
  return (
    <div
      className={cn(
        "h-24 w-32 rounded-md bg-slate-200 dark:bg-slate-700 animate-pulse",
        "overflow-hidden",
        className
      )}
      {...props}
    />
  );
}

export function SkeletonHeading({
  className,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h2
      className={cn(
        "h-6 w-full rounded-blg bg-slate-200 dark:bg-slate-700 animate-pulse",
        className
      )}
      {...props}
    />
  );
}

export function SkeletonText({
  className,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={cn(
        "h-4 w-full rounded-md bg-slate-200 dark:bg-slate-700 animate-pulse",
        className
      )}
      {...props}
    />
  );
}

export function SkeletonProgress({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "h-2 rounded-full bg-slate-200 dark:bg-slate-700 animate-pulse",
        "overflow-hidden",
        className
      )}
      {...props}
    />
  );
}

export function SkeletonTableRow({
  className,
  ...props
}: React.HTMLAttributes<HTMLTableRowElement>) {
  return (
    <tr
      className={cn(
        "border-b bg-slate-100 dark:bg-slate-800 hover:bg-slate-200/50 animate-pulse",
        className
      )}
      {...props}
    />
  );
}

export function SkeletonButton({
  className,
  ...props
}: React.HTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-lg bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 animate-pulse px-4 py-2 text-sm font-medium",
        className
      )}
      {...props}
    />
  );
}