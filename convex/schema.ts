import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  persons: defineTable({
    person_id: v.number(),
    name: v.string(),
    email: v.optional(v.string()),
    phone: v.optional(v.string()),
  }),
});