import { useParams } from "wouter";
import { useQuery } from "@tanstack/react-query";
import type { Hostel } from "@shared/schema";
import { useState } from "react";
import Navbar from "@/components/navbar";
import BookingModal from "@/components/booking-modal";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Star, MapPin, Phone, Wifi, Shield, ChefHat, Car } from "lucide-react";

export default function HostelDetails() {
  const { id } = useParams();
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);

  const { data: hostel, isLoading } = useQuery<Hostel>({
    queryKey: ["/api/hostels", id],
    queryFn: async () => {
      const response = await fetch(`/api/hostels/${id}`);
      if (!response.ok) throw new Error("Failed to fetch hostel");
      return response.json();
    },
  });

  const getAmenityIcon = (amenity: string) => {
    switch (amenity.toLowerCase()) {
      case "wifi":
        return <Wifi className="w-4 h-4" />;
      case "security":
        return <Shield className="w-4 h-4" />;
      case "kitchen":
        return <ChefHat className="w-4 h-4" />;
      case "parking":
        return <Car className="w-4 h-4" />;
      default:
        return null;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Skeleton className="w-full h-96 rounded-xl" />
            <div className="space-y-4">
              <Skeleton className="h-8 w-64" />
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-20 w-full" />
              <div className="flex gap-2">
                <Skeleton className="h-6 w-16" />
                <Skeleton className="h-6 w-20" />
                <Skeleton className="h-6 w-18" />
              </div>
              <Skeleton className="h-12 w-32" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!hostel) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Card>
            <CardContent className="pt-6 text-center">
              <h1 className="text-2xl font-bold text-slate-900 mb-2">Hostel Not Found</h1>
              <p className="text-slate-600">The hostel you're looking for doesn't exist.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div>
            <img 
              src={hostel.imageUrl} 
              alt={hostel.name}
              className="w-full h-96 object-cover rounded-xl shadow-lg"
            />
          </div>
          
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 mb-2">{hostel.name}</h1>
              <div className="flex items-center text-slate-600 mb-4">
                <MapPin className="w-5 h-5 mr-2 text-blue-600" />
                <span>{hostel.distance}</span>
              </div>
              <div className="flex items-center mb-4">
                <div className="flex text-yellow-400 mr-2">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className={`w-5 h-5 ${i < Math.floor(parseFloat(hostel.rating)) ? 'fill-current' : ''}`} />
                  ))}
                </div>
                <span className="text-slate-600">{hostel.rating} ({hostel.reviewCount} reviews)</span>
              </div>
            </div>

            <div>
              <p className="text-slate-700 text-lg leading-relaxed">{hostel.description}</p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-slate-900 mb-3">Amenities</h3>
              <div className="flex flex-wrap gap-2">
                {hostel.amenities.map((amenity, index) => (
                  <Badge key={index} variant="secondary" className="flex items-center gap-1">
                    {getAmenityIcon(amenity)}
                    {amenity}
                  </Badge>
                ))}
              </div>
            </div>

            <div className="bg-slate-50 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-slate-600">Monthly Rent</span>
                <span className="text-3xl font-bold text-slate-900">UGX {hostel.price.toLocaleString()}</span>
              </div>
              <div className="flex items-center text-slate-600 mb-4">
                <Phone className="w-4 h-4 mr-2" />
                <span>{hostel.contact}</span>
              </div>
              <Button 
                className="w-full bg-blue-600 hover:bg-blue-700"
                onClick={() => setIsBookingModalOpen(true)}
              >
                Book Now
              </Button>
            </div>
          </div>
        </div>

        <Card>
          <CardContent className="pt-6">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Location & Contact</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-slate-900 mb-2">Address</h3>
                <p className="text-slate-600">{hostel.address}</p>
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 mb-2">Contact Information</h3>
                <p className="text-slate-600">{hostel.contact}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <BookingModal 
        isOpen={isBookingModalOpen}
        onClose={() => setIsBookingModalOpen(false)}
        hostel={hostel}
      />
    </div>
  );
}
