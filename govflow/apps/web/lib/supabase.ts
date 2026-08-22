"use client";

import { createServerClient, type SupabaseClient } from "@supabase/ssr";
import { type Database } from "@/types/supabase";
import { type NextRequest, type NextResponse } from "next/server";
import { cookies } from "next/headers";

// Create a single supa client instance for reusing across server components.
export function createSupabaseClient(): SupabaseClient<Database> {
  return createServerClient<
    Database,
    Database["public"]["Tables"]["%"]["Row"]
  >(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookies().get(name)?.value;
        },
        set(name: string, value: string, options: any) {
          return cookies().set(name, value, options);
        },
        remove(name: string, options: any) {
          return cookies().delete(name, options);
        },
      },
    }
  );
}

// Type-safe supabase client instance (initialized per-request in middleware or route handlers)
export const supabase = createServerClient<Database>(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  {
    cookies: {
      get(name: string) {
        const cookieStore = cookies();
        return cookieStore.get(name)?.value;
      },
      set(name: string, value: string, options: any) {
        const cookieStore = cookies();
        return cookieStore.set(name, value, options);
      },
      remove(name: string, options: any) {
        const cookieStore = cookies();
        return cookieStore.delete(name, options);
      },
    },
  }
);

// Auth helpers
export type { User, Session, AuthError } from "@supabase/ssr";

export async function getSession() {
  const {
    data: { session },
    error,
  } = await supabase.auth.getSession();
  return { session, error };
}

export async function signInWithPassword(email: string, password: string) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });
  return { data, error };
}

export async function signUp(email: string, password: string) {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
  });
  return { data, error };
}

export async function signOut() {
  const { error } = await supabase.auth.signOut();
  return { error };
}