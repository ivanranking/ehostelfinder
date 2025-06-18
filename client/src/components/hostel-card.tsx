import { Link } from "wouter";
import type { Hostel } from "@shared/schema";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Star, MapPin } from "lucide-react";

interface HostelCardProps {
  hostel: Hostel;
  onBookingClick: (hostel: Hostel) => void;
}

export default function HostelCard({ hostel, onBookingClick }: HostelCardProps) {
  return (
    <Card className="overflow-hidden hover:shadow-md transition-shadow cursor-pointer">
      <div className="flex flex-col md:flex-row">
        <img 
          src={hostel.imageUrl} 
          alt={hostel.name}
          className="w-full md:w-80 h-64 object-cover"
        />
        <CardContent className="p-6 flex-1">
          <div className="flex justify-between items-start mb-3">
            <div>
              <h3 className="text-xl font-semibold text-slate-900 mb-1">
                {hostel.name}
              </h3>
              <p className="text-slate-600 flex items-center">
                <MapPin className="w-4 h-4 mr-2 text-blue-600" />
                <span>{hostel.distance}</span>
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-slate-900">
                UGX {hostel.price.toLocaleString()}
              </div>
              <div className="text-sm text-slate-600">per month</div>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-2 mb-4">
            {hostel.amenities.map((amenity, index) => (
              <Badge key={index} variant="secondary" className="bg-green-100 text-green-800">
                {amenity}
              </Badge>
            ))}
          </div>
          
          <p className="text-slate-600 mb-4 line-clamp-3">
            {hostel.description}
          </p>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="flex text-yellow-400 mr-2">
                {[...Array(5)].map((_, i) => (
                  <Star 
                    key={i} 
                    className={`w-4 h-4 ${i < Math.floor(parseFloat(hostel.rating)) ? 'fill-current' : ''}`} 
                  />
                ))}
              </div>
              <span className="text-sm text-slate-600">
                {hostel.rating} ({hostel.reviewCount} reviews)
              </span>
            </div>
            <div className="flex space-x-2">
              <Link href={`/hostel/${hostel.id}`}>
                <Button variant="outline" className="border-blue-600 text-blue-600 hover:bg-blue-50">
                  View Details
                </Button>
              </Link>
              <Button 
                className="bg-blue-600 hover:bg-blue-700 text-white"
                onClick={() => onBookingClick(hostel)}
              >
                Book Now
              </Button>
            </div>
          </div>
        </CardContent>
      </div>
    </Card>
  );
}
