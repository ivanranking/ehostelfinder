import { pgTable, text, serial, integer, boolean, decimal, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const hostels = pgTable("hostels", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description").notNull(),
  university: text("university").notNull(), // "Makerere University" or "MUBS"
  distance: text("distance").notNull(), // e.g., "0.8km from Makerere University"
  price: integer("price").notNull(), // in UGX
  rating: decimal("rating", { precision: 2, scale: 1 }).notNull(),
  reviewCount: integer("review_count").notNull().default(0),
  imageUrl: text("image_url").notNull(),
  amenities: text("amenities").array().notNull(), // ["WiFi", "Security", "Kitchen", etc.]
  contact: text("contact").notNull(),
  address: text("address").notNull(),
  available: boolean("available").notNull().default(true),
  createdAt: timestamp("created_at").defaultNow(),
});

export const bookings = pgTable("bookings", {
  id: serial("id").primaryKey(),
  hostelId: integer("hostel_id").notNull(),
  fullName: text("full_name").notNull(),
  email: text("email").notNull(),
  phone: text("phone").notNull(),
  university: text("university").notNull(),
  studentId: text("student_id").notNull(),
  moveInDate: text("move_in_date").notNull(),
  roomType: text("room_type").notNull(),
  specialRequests: text("special_requests"),
  status: text("status").notNull().default("pending"), // "pending", "confirmed", "cancelled"
  createdAt: timestamp("created_at").defaultNow(),
});

export const insertHostelSchema = createInsertSchema(hostels).omit({
  id: true,
  createdAt: true,
});

export const insertBookingSchema = createInsertSchema(bookings).omit({
  id: true,
  createdAt: true,
  status: true,
});

export type InsertHostel = z.infer<typeof insertHostelSchema>;
export type Hostel = typeof hostels.$inferSelect;
export type InsertBooking = z.infer<typeof insertBookingSchema>;
export type Booking = typeof bookings.$inferSelect;
