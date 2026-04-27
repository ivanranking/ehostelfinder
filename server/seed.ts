import { storage } from "./storage";
import type { InsertHostel } from "@shared/schema";

const seedHostels: InsertHostel[] = [
  {
    name: "University Gardens Hostel",
    description: "Modern hostel with spacious rooms, 24/7 security, and excellent facilities. Perfect for serious students.",
    university: "Makerere University",
    distance: "0.8km from Makerere University",
    price: 300000,
    rating: 4.8,
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
    rating: 4.3,
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
    university: "MUBS",
    distance: "1.0km from MUBS",
    price: 400000,
    rating: 4.9,
    reviewCount: 31,
    imageUrl: "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600",
    amenities: ["Premium", "AC", "Gym", "WiFi"],
    contact: "+256 700 345678",
    address: "Nakawa, Kampala",
    available: true,
  },
];

export async function seedHostelsIfEmpty() {
  const currentHostels = await storage.getAllHostels();
  if (currentHostels.length > 0) {
    return;
  }

  for (const hostel of seedHostels) {
    await storage.createHostel(hostel);
  }
}
