import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const getLanes = query({
    handler: async (ctx) => {
        const lanes = await ctx.db.query("lanes").collect();
        return Promise.all(
            lanes.map(async (lane) => {
                const origin = await ctx.db.get(lane.originPortId);
                const destination = await ctx.db.get(lane.destinationPortId);
                return {
                    ...lane,
                    origin_port: origin,
                    destination_port: destination,
                };
            })
        );
    },
});

export const getAlerts = query({
    handler: async (ctx) => {
        return await ctx.db
            .query("alerts")
            .order("desc")
            .take(50);
    },
});

export const getRiskScores = query({
    handler: async (ctx) => {
        return await ctx.db.query("riskScores").collect();
    },
});

// Seed data mutation
export const seedInitialData = mutation({
    handler: async (ctx) => {
        // Check if ports exist
        const existingPorts = await ctx.db.query("ports").collect();
        if (existingPorts.length > 0) return;

        // Add some base ports
        const portIds = [];
        const ports = [
            { name: "Shanghai", unlocode: "CNSHA", latitude: 31.2304, longitude: 121.4737, country: "China", region: "East Asia" },
            { name: "Rotterdam", unlocode: "NLRTM", latitude: 51.9225, longitude: 4.47917, country: "Netherlands", region: "Europe" },
            { name: "Singapore", unlocode: "SGSIN", latitude: 1.3521, longitude: 103.8198, country: "Singapore", region: "Southeast Asia" }
        ];

        for (const p of ports) {
            const id = await ctx.db.insert("ports", p);
            portIds.push(id);
        }

        // Add a lane
        await ctx.db.insert("lanes", {
            originPortId: portIds[0],
            destinationPortId: portIds[1],
            mode: "ocean"
        });
    }
});
