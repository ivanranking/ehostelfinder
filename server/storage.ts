import { hostels, bookings, users, messages, type Hostel, type InsertHostel, type Booking, type InsertBooking, type User, type UpsertUser, type InsertMessage, type Message } from "@shared/schema";
import { db } from "./db";
import { eq } from "drizzle-orm";

export interface IStorage {
  // Hostel operations
  getAllHostels(): Promise<Hostel[]>;
  getHostelById(id: number): Promise<Hostel | undefined>;
  getHostelsByUniversity(university: string): Promise<Hostel[]>;
  createHostel(hostel: InsertHostel): Promise<Hostel>;
  
  // Booking operations
  createBooking(booking: InsertBooking): Promise<Booking>;
  getBookingById(id: number): Promise<Booking | undefined>;
  getBookingsByHostel(hostelId: number): Promise<Booking[]>;

  // Message operations
  createMessage(message: InsertMessage): Promise<Message>;
  getMessagesByHostel(hostelId: number): Promise<Message[]>;
  
  // User operations (required for Replit Auth)
  getUser(id: string): Promise<User | undefined>;
  upsertUser(user: UpsertUser): Promise<User>;
}

export class DatabaseStorage implements IStorage {
  async getAllHostels(): Promise<Hostel[]> {
    return await db.select().from(hostels);
  }

  async getHostelById(id: number): Promise<Hostel | undefined> {
    const [hostel] = await db.select().from(hostels).where(eq(hostels.id, id));
    return hostel || undefined;
  }

  async getHostelsByUniversity(university: string): Promise<Hostel[]> {
    return await db.select().from(hostels).where(eq(hostels.university, university));
  }

  async createHostel(insertHostel: InsertHostel): Promise<Hostel> {
    const [hostel] = await db
      .insert(hostels)
      .values(insertHostel)
      .returning();
    return hostel;
  }

  async createBooking(insertBooking: InsertBooking): Promise<Booking> {
    const [booking] = await db
      .insert(bookings)
      .values(insertBooking)
      .returning();
    return booking;
  }

  async getBookingById(id: number): Promise<Booking | undefined> {
    const [booking] = await db.select().from(bookings).where(eq(bookings.id, id));
    return booking || undefined;
  }

  async getBookingsByHostel(hostelId: number): Promise<Booking[]> {
    return await db.select().from(bookings).where(eq(bookings.hostelId, hostelId));
  }

  async createMessage(insertMessage: InsertMessage): Promise<Message> {
    const [message] = await db
      .insert(messages)
      .values(insertMessage)
      .returning();
    return message;
  }

  async getMessagesByHostel(hostelId: number): Promise<Message[]> {
    return await db.select().from(messages).where(eq(messages.hostelId, hostelId));
  }

  async getUser(id: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user;
  }

  async upsertUser(userData: UpsertUser): Promise<User> {
    const [user] = await db
      .insert(users)
      .values(userData)
      .onConflictDoUpdate({
        target: users.id,
        set: {
          ...userData,
          updatedAt: new Date(),
        },
      })
      .returning();
    return user;
  }
}

export const storage = new DatabaseStorage();
