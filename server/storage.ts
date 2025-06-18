import { hostels, bookings, type Hostel, type InsertHostel, type Booking, type InsertBooking } from "@shared/schema";

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
}

export class MemStorage implements IStorage {
  private hostels: Map<number, Hostel>;
  private bookings: Map<number, Booking>;
  private currentHostelId: number;
  private currentBookingId: number;

  constructor() {
    this.hostels = new Map();
    this.bookings = new Map();
    this.currentHostelId = 1;
    this.currentBookingId = 1;
    this.seedData();
  }

  private seedData() {
    const sampleHostels: InsertHostel[] = [
      {
        name: "University Gardens Hostel",
        description: "Modern hostel with spacious rooms, 24/7 security, and excellent facilities. Perfect for serious students.",
        university: "Makerere University",
        distance: "0.8km from Makerere University",
        price: 300000,
        rating: "4.8",
        reviewCount: 24,
        imageUrl: "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600",
        amenities: ["WiFi", "Security", "Kitchen", "Laundry"],
        contact: "+256 700 123456",
        address: "Wandegeya, Kampala",
        available: true,
      },
      {
        name: "Scholars Inn",
        description: "Affordable accommodation with dedicated study areas and quiet environment ideal for academic focus.",
        university: "Makerere University",
        distance: "1.2km from Makerere University",
        price: 250000,
        rating: "4.3",
        reviewCount: 18,
        imageUrl: "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600",
        amenities: ["WiFi", "Study Rooms", "Parking"],
        contact: "+256 700 789012",
        address: "Kikoni, Kampala",
        available: true,
      },
      {
        name: "Campus View Hostel",
        description: "Premium accommodation with air conditioning, gym facilities, and stunning campus views.",
        university: "Makerere University",
        distance: "0.5km from Makerere University",
        price: 400000,
        rating: "4.9",
        reviewCount: 31,
        imageUrl: "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600",
        amenities: ["Premium", "AC", "Gym", "WiFi"],
        contact: "+256 700 345678",
        address: "Makerere Hill, Kampala",
        available: true,
      },
      {
        name: "MUBS Executive Lodge",
        description: "Executive accommodation near MUBS with modern amenities and professional environment.",
        university: "MUBS",
        distance: "0.3km from MUBS",
        price: 350000,
        rating: "4.6",
        reviewCount: 22,
        imageUrl: "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600",
        amenities: ["WiFi", "Security", "Parking", "Laundry"],
        contact: "+256 700 456789",
        address: "Nakawa, Kampala",
        available: true,
      },
      {
        name: "Business Students Haven",
        description: "Tailored for business students with conference rooms and networking spaces.",
        university: "MUBS",
        distance: "0.7km from MUBS",
        price: 280000,
        rating: "4.4",
        reviewCount: 15,
        imageUrl: "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600",
        amenities: ["WiFi", "Conference Room", "Kitchen", "Security"],
        contact: "+256 700 567890",
        address: "Nakawa Industrial Area, Kampala",
        available: true,
      },
    ];

    sampleHostels.forEach(hostel => {
      this.createHostel(hostel);
    });
  }

  async getAllHostels(): Promise<Hostel[]> {
    return Array.from(this.hostels.values());
  }

  async getHostelById(id: number): Promise<Hostel | undefined> {
    return this.hostels.get(id);
  }

  async getHostelsByUniversity(university: string): Promise<Hostel[]> {
    return Array.from(this.hostels.values()).filter(
      hostel => hostel.university === university
    );
  }

  async createHostel(insertHostel: InsertHostel): Promise<Hostel> {
    const id = this.currentHostelId++;
    const hostel: Hostel = {
      ...insertHostel,
      id,
      createdAt: new Date(),
    };
    this.hostels.set(id, hostel);
    return hostel;
  }

  async createBooking(insertBooking: InsertBooking): Promise<Booking> {
    const id = this.currentBookingId++;
    const booking: Booking = {
      ...insertBooking,
      id,
      status: "pending",
      createdAt: new Date(),
    };
    this.bookings.set(id, booking);
    return booking;
  }

  async getBookingById(id: number): Promise<Booking | undefined> {
    return this.bookings.get(id);
  }

  async getBookingsByHostel(hostelId: number): Promise<Booking[]> {
    return Array.from(this.bookings.values()).filter(
      booking => booking.hostelId === hostelId
    );
  }
}

export const storage = new MemStorage();
