'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Ship, Globe, Bell, ShieldCheck, Palette, LayoutDashboard, Search, Filter } from 'lucide-react';
import { Sidebar } from '@/components/layout/Sidebar';
import { GeoRiskNavigator, GeoRiskData } from '@/components/ai/GeoRiskNavigator';

// Mock Scenarios for Design Preview
const DEMO_SCENARIOS = {
    lowRisk: {
        route: 'London → Rotterdam',
        data: {
            score: 15,
            level: 'LOW' as const,
            advisory: 'Route appears stable. Standard procedures apply.',
            factors: {
                zone: {
                    score: 10,
                    weight: 0.4,
                    details: []
                },
                sanctions: {
                    score: 0,
                    weight: 0.4,
                    details: [],
                    available: true
                },
                weather: {
                    score: 5,
                    weight: 0.2,
                    details: {
                        description: 'clear sky',
                        windSpeed: 5,
                        visibility: 10000,
                        temp: 15,
                        factors: []
                    },
                    available: true
                }
            },
            premium: true,
            lastUpdated: Date.now()
        }
    },
    mediumRisk: {
        route: 'Mumbai → Rotterdam (via Suez)',
        data: {
            score: 68,
            level: 'MEDIUM' as const,
            advisory: 'Elevated risk factors detected. Review routing options and prepare contingency plans where applicable.',
            factors: {
                zone: {
                    score: 55,
                    weight: 0.4,
                    details: [
                        'Transit via Suez Canal - elevated maritime risk',
                        'Destination region has moderate geopolitical instability'
                    ]
                },
                sanctions: {
                    score: 0,
                    weight: 0.4,
                    details: [],
                    available: true
                },
                weather: {
                    score: 15,
                    weight: 0.2,
                    details: {
                        description: 'light rain',
                        windSpeed: 12,
                        visibility: 8000,
                        temp: 18,
                        factors: ['Moderate winds (12 m/s)']
                    },
                    available: true
                }
            },
            premium: true,
            lastUpdated: Date.now()
        }
    },
    highRisk: {
        route: 'Dubai → Tehran',
        data: {
            score: 88,
            level: 'HIGH' as const,
            advisory: 'Significant risk factors detected. Consider alternative routing, additional insurance, or enhanced due diligence before proceeding.',
            factors: {
                zone: {
                    score: 80,
                    weight: 0.4,
                    details: [
                        'Destination (Iran) is under sanctions',
                        'Transit via Strait of Hormuz - elevated maritime risk',
                        'Destination region has active geopolitical tensions'
                    ]
                },
                sanctions: {
                    score: 35,
                    weight: 0.4,
                    details: [
                        {
                            party: 'Sample Shipping Co.',
                            matched: true,
                            entities: [{
                                name: 'Sample Shipping Co.',
                                type: 'LegalEntity',
                                source: 'OFAC, EU',
                                score: 0.95
                            }]
                        }
                    ],
                    available: true
                },
                weather: {
                    score: 25,
                    weight: 0.2,
                    details: {
                        description: 'dust storm',
                        windSpeed: 25,
                        visibility: 2000,
                        temp: 42,
                        factors: ['Strong winds (25 m/s)', 'Low visibility']
                    },
                    available: true
                }
            },
            premium: true,
            lastUpdated: Date.now()
        }
    },
    severeRisk: {
        route: 'Odessa → Istanbul',
        data: {
            score: 95,
            level: 'HIGH' as const,
            advisory: 'CRITICAL ROUTE SUSPENSION ADVISED. Active conflict zone with live kinetic threats detected.',
            factors: {
                zone: {
                    score: 100,
                    weight: 0.5,
                    details: [
                        'Black Sea Grain Corridor Suspended',
                        'Active Naval Blockade Reported',
                        'Floating Mine Drift Warning'
                    ]
                },
                sanctions: {
                    score: 45,
                    weight: 0.3,
                    details: [],
                    available: true
                },
                weather: {
                    score: 10,
                    weight: 0.2,
                    details: {
                        description: 'overcast',
                        windSpeed: 8,
                        visibility: 9000,
                        temp: 12,
                        factors: []
                    },
                    available: true
                }
            },
            premium: true,
            lastUpdated: Date.now()
        }
    }
};

export default function GeoRiskDesignPage() {
    const [selectedScenario, setSelectedScenario] = useState<keyof typeof DEMO_SCENARIOS>('mediumRisk');

    return (
        <div className="flex h-screen bg-white font-sans text-gray-600 overflow-hidden">
            <Sidebar />

            {/* Main Content */}
            <main className="flex-1 flex flex-col relative overflow-hidden">
                {/* Header */}
                <header className="h-14 border-b border-gray-200 bg-white flex items-center justify-between px-6 z-20">
                    <div className="flex items-center gap-4">
                        <h1 className="text-sm font-normal text-black tracking-tight">GeoRisk Navigator</h1>
                        <span className="px-1.5 py-0.5 rounded text-[9px] bg-gray-100 text-gray-500 border border-gray-200 font-normal tracking-wide">
                            MOCK DATA
                        </span>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search..."
                                className="h-8 pl-8 pr-3 bg-gray-50 border border-gray-200 rounded-md text-xs text-gray-700 focus:outline-none focus:border-gray-400 w-44 transition-colors"
                            />
                        </div>
                    </div>
                </header>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
                    {/* Scenario Selector */}
                    <div className="bg-gray-50 rounded-lg border border-gray-200 p-4 mb-6">
                        <h2 className="text-[9px] font-normal text-gray-400 uppercase tracking-widest mb-3">
                            Select Scenario
                        </h2>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                            {Object.entries(DEMO_SCENARIOS).map(([key, scenario]) => (
                                <button
                                    key={key}
                                    onClick={() => setSelectedScenario(key as keyof typeof DEMO_SCENARIOS)}
                                    className={`p-2.5 rounded-md border transition-all text-left ${selectedScenario === key
                                        ? 'border-gray-400 bg-white'
                                        : 'border-gray-200 hover:border-gray-300 bg-white'
                                        }`}
                                >
                                    <div className="text-xs font-normal text-black mb-0.5">
                                        {key === 'lowRisk' && '✓ Low Risk'}
                                        {key === 'mediumRisk' && '⚠ Medium Risk'}
                                        {key === 'highRisk' && '⛔ High Risk'}
                                        {key === 'severeRisk' && '☠ Severe Risk'}
                                    </div>
                                    <div className="text-[10px] text-gray-400 truncate">
                                        {scenario.route}
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Component Render */}
                    <GeoRiskNavigator
                        route={DEMO_SCENARIOS[selectedScenario].route}
                        data={DEMO_SCENARIOS[selectedScenario].data as GeoRiskData}
                    />
                </div>
            </main>
        </div>
    );
}
