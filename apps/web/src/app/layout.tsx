import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";
import { ClerkProvider } from "@clerk/nextjs";
import { ConvexClientProvider } from "@/components/ConvexClientProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "GeoRisk | Premium Risk Advisory",
    description: "Predict disruption risk on your freight routes.",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <ClerkProvider>
            <html lang="en">
                <body className={cn(inter.className, "min-h-screen bg-slate-50")} suppressHydrationWarning>
                    <ConvexClientProvider>{children}</ConvexClientProvider>
                </body>
            </html>
        </ClerkProvider>
    );
}

