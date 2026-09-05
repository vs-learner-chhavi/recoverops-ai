import type { Metadata } from "next";
import { createElement, type ReactNode } from "react";
// @ts-expect-error Next.js processes this global stylesheet import at build time.
import "./globals.css";

export const metadata: Metadata = {
  title: "RecoverOps AI — Revenue Recovery Engine",
  description:
    "Autonomous Multi-Tier Revenue Recovery Engine with Explainable AI Diagnostics",
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return createElement(
    "html",
    { lang: "en", className: "dark" },
    createElement("body", { className: "min-h-screen antialiased" }, children),
  );
}