import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { insertBookingSchema } from "@shared/schema";
import { z } from "zod";
import { setupAuth, isAuthenticated } from "./replitAuth";

export async function registerRoutes(app: Express): Promise<Server> {
  // Auth middleware
  await setupAuth(app);

  // Auth routes
  app.get('/api/auth/user', isAuthenticated, async (req: any, res) => {
    try {
      const userId = req.user.claims.sub;
      const user = await storage.getUser(userId);
      res.json(user);
    } catch (error) {
      console.error("Error fetching user:", error);
      res.status(500).json({ message: "Failed to fetch user" });
    }
  });
  // Get all hostels
  app.get("/api/hostels", async (req, res) => {
    try {
      const { university } = req.query;
      
      let hostels;
      if (university && university !== "All Universities") {
        hostels = await storage.getHostelsByUniversity(university as string);
      } else {
        hostels = await storage.getAllHostels();
      }
      
      res.json(hostels);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch hostels" });
    }
  });

  // Get hostel by ID
  app.get("/api/hostels/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const hostel = await storage.getHostelById(id);
      
      if (!hostel) {
        return res.status(404).json({ error: "Hostel not found" });
      }
      
      res.json(hostel);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch hostel" });
    }
  });

  // Create booking (protected route)
  app.post("/api/bookings", isAuthenticated, async (req: any, res) => {
    try {
      const validatedData = insertBookingSchema.parse(req.body);
      
      // Check if hostel exists
      const hostel = await storage.getHostelById(validatedData.hostelId);
      if (!hostel) {
        return res.status(404).json({ error: "Hostel not found" });
      }
      
      const booking = await storage.createBooking(validatedData);
      res.status(201).json(booking);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: "Invalid booking data", details: error.errors });
      }
      res.status(500).json({ error: "Failed to create booking" });
    }
  });

  // Get booking by ID
  app.get("/api/bookings/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const booking = await storage.getBookingById(id);
      
      if (!booking) {
        return res.status(404).json({ error: "Booking not found" });
      }
      
      res.json(booking);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch booking" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
