import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Breadcrumb } from "@/components/common/breadcrumb";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Settings,
  User,
  Bell,
  Shield,
  Globe,
  Moon,
  Sun,
  ChevronRight,
} from "lucide-react";

const settingsSections = [
  {
    id: "profile",
    title: "Profile Settings",
    description: "Manage your personal information and preferences",
    icon: User,
    href: "/settings/profile",
  },
  {
    id: "notifications",
    title: "Notification Preferences",
    description: "Configure how you receive updates and alerts",
    icon: Bell,
    href: "/settings/notifications",
  },
  {
    id: "security",
    title: "Security & Privacy",
    description: "Manage passwords, 2FA, and privacy settings",
    icon: Shield,
    href: "/settings/security",
  },
  {
    id: "language",
    title: "Language & Region",
    description: "Set your preferred language and regional formats",
    icon: Globe,
    href: "/settings/language",
  },
];

export default function SettingsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <Breadcrumb />

        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Settings
          </h1>
          <p className="mt-1 text-slate-600 dark:text-slate-400">
            Manage your account settings and preferences
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sun className="h-5 w-5" />
              Appearance
            </CardTitle>
            <CardDescription>
              Customize the look and feel of the application
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <Button variant="outline">
                <Sun className="mr-2 h-4 w-4" />
                Light
              </Button>
              <Button variant="outline">
                <Moon className="mr-2 h-4 w-4" />
                Dark
              </Button>
              <Button variant="outline">System</Button>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-4">
          {settingsSections.map((section) => (
            <Card key={section.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-4">
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gov-blue/10">
                    <section.icon className="h-5 w-5 text-gov-blue" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-slate-900 dark:text-white">
                      {section.title}
                    </p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {section.description}
                    </p>
                  </div>
                  <Button variant="ghost" size="icon" asChild>
                    <a href={section.href}>
                      <ChevronRight className="h-5 w-5" />
                    </a>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card className="border-red-200 dark:border-red-900">
          <CardHeader>
            <CardTitle className="text-red-600">Danger Zone</CardTitle>
            <CardDescription>
              Irreversible actions for your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-slate-900 dark:text-white">
                  Delete Account
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Permanently delete your account and all associated data
                </p>
              </div>
              <Button variant="destructive">Delete Account</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
