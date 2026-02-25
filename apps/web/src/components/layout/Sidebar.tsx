"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ShieldCheck, LayoutDashboard, Globe, Ship, Bell, Palette } from 'lucide-react';
import { UserButton, useUser } from '@clerk/nextjs';
import { cn } from '@/lib/utils';

export const Sidebar = () => {
    const pathname = usePathname();
    const { user } = useUser();

    const navItems: { href: string; label: string; icon: any; disabled?: boolean }[] = [
        { href: "/", label: "Dashboard", icon: LayoutDashboard },
        { href: "/global-map", label: "Global Map", icon: Globe },
        { href: "/assets", label: "Assets", icon: Ship },
        { href: "/intel-feed", label: "Intel Feed", icon: Bell },
    ];

    const bottomItems = [
        { href: "/georisk-design", label: "Design System", icon: Palette },
    ];

    return (
        <aside className="w-60 border-r border-gray-200 bg-gray-50 flex flex-col z-30 h-screen">
            <div className="h-14 flex items-center px-5 border-b border-gray-200">
                <div className="flex items-center gap-2 text-black">
                    <ShieldCheck className="h-5 w-5 text-gray-700" />
                    <span className="font-normal text-sm tracking-tight text-gray-900">GeoRisk <span className="text-black font-semibold">Pro</span></span>
                </div>
            </div>

            <div className="p-4 space-y-1">
                <p className="px-3 text-[9px] font-normal text-gray-400 uppercase tracking-widest mb-2">Platform</p>
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href;

                    return (
                        <Link
                            key={item.label}
                            href={item.disabled ? "#" : item.href}
                            className={cn(
                                "w-full flex items-center gap-2 px-3 py-1.5 text-xs font-normal transition-colors rounded-md",
                                isActive
                                    ? "text-black bg-gray-100 border border-gray-200"
                                    : "text-gray-500 hover:text-black hover:bg-gray-100",
                                item.disabled && "opacity-50 cursor-not-allowed pointer-events-none"
                            )}
                        >
                            <Icon className={cn("h-3.5 w-3.5", isActive ? "text-gray-700" : "text-gray-400")} />
                            {item.label}
                        </Link>
                    );
                })}
            </div>

            <div className="mt-auto p-3 border-t border-gray-200">
                {bottomItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href;

                    return (
                        <Link
                            key={item.label}
                            href={item.href}
                            className={cn(
                                "w-full flex items-center gap-2 px-3 py-1.5 text-xs font-normal transition-colors rounded-md mb-2",
                                isActive
                                    ? "text-black bg-gray-100 border border-gray-200"
                                    : "text-gray-500 hover:text-black hover:bg-gray-100"
                            )}
                        >
                            <Icon className={cn("h-3.5 w-3.5", isActive ? "text-gray-700" : "text-gray-400")} />
                            {item.label}
                        </Link>
                    );
                })}

                <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-md border border-gray-200">
                    <UserButton />
                    <div className="flex flex-col">
                        <span className="text-[11px] font-normal text-gray-700 truncate max-w-[100px]">{user?.fullName || 'User'}</span>
                        <span className="text-[9px] text-gray-400">Enterprise</span>
                    </div>
                </div>
            </div>
        </aside>
    );
};
