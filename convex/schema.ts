import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
    users: defineTable({
        name: v.string(),
        email: v.string(),
        tokenIdentifier: v.string(), // Clerk's user ID
        orgRole: v.optional(v.string()), // e.g., "admin", "agent"
    }).index("by_token", ["tokenIdentifier"]),

    ports: defineTable({
        unlocode: v.string(),
        name: v.string(),
        latitude: v.number(),
        longitude: v.number(),
        country: v.string(),
        region: v.string(),
    }).index("by_unlocode", ["unlocode"]),

    lanes: defineTable({
        originPortId: v.id("ports"),
        destinationPortId: v.id("ports"),
        mode: v.union(v.literal("ocean"), v.literal("air"), v.literal("rail")),
        ownerId: v.optional(v.id("users")),
    }),

    riskEvents: defineTable({
        type: v.string(), // "weather", "news", "sanction"
        severity: v.string(), // "low", "medium", "high", "severe"
        source: v.string(),
        externalId: v.string(),
        title: v.string(),
        description: v.string(),
        impactedEntityIds: v.array(v.id("ports")),
        startsAt: v.string(),
        endsAt: v.optional(v.string()),
    }).index("by_type", ["type"]),

    riskScores: defineTable({
        entityType: v.string(), // "lane", "port"
        entityId: v.string(), // ID from ports or lanes
        score: v.number(),
        status: v.string(),
        breakdown: v.any(), // JSON-like object
        updatedAt: v.string(),
    }).index("by_entity", ["entityType", "entityId"]),

    alerts: defineTable({
        title: v.string(),
        message: v.string(),
        severity: v.string(),
        impactedLaneIds: v.array(v.id("lanes")),
        isRead: v.boolean(),
        createdAt: v.string(),
    }),
});
