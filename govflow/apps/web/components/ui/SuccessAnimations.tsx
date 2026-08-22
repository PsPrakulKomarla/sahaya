export interface SuccessConfig {
  variant?: "default" | "gov" | "success";
  title?: string;
  description?: string;
}

export const SUCCESS_VARIANTS = {
  default: "bg-white dark:bg-slate-800",
  gov: "bg-white dark:bg-slate-800 border-l-4 border-gov-blue",
  success: "bg-green-100 dark:bg-green-900/30",
} as const;