import { query } from "./_generated/server";
import { v } from "convex/values";

export const findMatches = query({
  args: {
    name: v.string(),
    email: v.string(),
    phone: v.string(),
  },

  handler: async (ctx, args) => {
    const people = await ctx.db.query("persons").collect();

    const name = args.name.trim().toLowerCase();
    const email = args.email.trim().toLowerCase();
    const phone = args.phone.replace(/\D/g, "");

    return people
      .filter((person) => {
        const nameMatch =
          person.name.trim().toLowerCase() === name;

        const emailMatch =
          person.email?.trim().toLowerCase() === email;

        const phoneMatch =
          person.phone?.replace(/\D/g, "") === phone;

        return nameMatch || emailMatch || phoneMatch;
      })
      .map((person) => ({
        person_id: person.person_id,
        name: person.name,
        email: person.email,
        phone: person.phone,
      }));
  },
});