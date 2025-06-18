import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import type { Hostel } from "@shared/schema";
import Navbar from "@/components/navbar";
import HeroSection from "@/components/hero-section";
import UniversityTabs from "@/components/university-tabs";
import FilterSidebar from "@/components/filter-sidebar";
import HostelCard from "@/components/hostel-card";
import BookingModal from "@/components/booking-modal";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useLocation } from "wouter";

export default function Home() {
  const [location] = useLocation();
  const [selectedUniversity, setSelectedUniversity] = useState("Makerere University");

  // Handle URL parameters for university filtering
  useEffect(() => {
    const urlParams = new URLSearchParams(location.split('?')[1] || '');
    const universityParam = urlParams.get('university');
    if (universityParam) {
      setSelectedUniversity(universityParam);
    }
  }, [location]);
  const [selectedHostel, setSelectedHostel] = useState<Hostel | null>(null);
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);
  const [filters, setFilters] = useState({
    priceRange: [] as string[],
    amenities: [] as string[],
    distance: [] as string[],
  });

  const { data: hostels, isLoading } = useQuery<Hostel[]>({
    queryKey: ["/api/hostels", selectedUniversity],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (selectedUniversity !== "All Universities") {
        params.append("university", selectedUniversity);
      }
      const response = await fetch(`/api/hostels?${params}`);
      if (!response.ok) throw new Error("Failed to fetch hostels");
      return response.json();
    },
  });

  const handleBookingClick = (hostel: Hostel) => {
    setSelectedHostel(hostel);
    setIsBookingModalOpen(true);
  };

  const filterHostels = (hostels: Hostel[] | undefined) => {
    if (!hostels) return [];
    
    return hostels.filter(hostel => {
      // Price filter
      if (filters.priceRange.length > 0) {
        const price = hostel.price;
        const matchesPrice = filters.priceRange.some(range => {
          switch (range) {
            case "under200":
              return price < 200000;
            case "200-400":
              return price >= 200000 && price <= 400000;
            case "400+":
              return price > 400000;
            default:
              return true;
          }
        });
        if (!matchesPrice) return false;
      }

      // Amenities filter
      if (filters.amenities.length > 0) {
        const hasAmenity = filters.amenities.some(amenity => 
          hostel.amenities.includes(amenity)
        );
        if (!hasAmenity) return false;
      }

      return true;
    });
  };

  const filteredHostels = filterHostels(hostels);

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <HeroSection />
      <UniversityTabs 
        selectedUniversity={selectedUniversity}
        onUniversityChange={setSelectedUniversity}
      />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12" id="hostels">
        <div className="flex flex-col lg:flex-row gap-8">
          <FilterSidebar filters={filters} onFiltersChange={setFilters} />
          
          <div className="flex-1">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-slate-900">
                Available Hostels near {selectedUniversity}
              </h2>
              <select className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                <option>Sort by: Recommended</option>
                <option>Price: Low to High</option>
                <option>Price: High to Low</option>
                <option>Distance</option>
              </select>
            </div>

            {isLoading ? (
              <div className="grid gap-6">
                {[1, 2, 3].map(i => (
                  <div key={i} className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                    <div className="flex flex-col md:flex-row">
                      <Skeleton className="w-full md:w-80 h-64" />
                      <div className="p-6 flex-1">
                        <Skeleton className="h-6 w-64 mb-2" />
                        <Skeleton className="h-4 w-48 mb-4" />
                        <div className="flex gap-2 mb-4">
                          <Skeleton className="h-6 w-16" />
                          <Skeleton className="h-6 w-20" />
                          <Skeleton className="h-6 w-18" />
                        </div>
                        <Skeleton className="h-20 w-full mb-4" />
                        <div className="flex justify-between">
                          <Skeleton className="h-6 w-32" />
                          <div className="flex gap-2">
                            <Skeleton className="h-10 w-24" />
                            <Skeleton className="h-10 w-24" />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : filteredHostels.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-slate-600 text-lg">No hostels found matching your criteria.</p>
                <Button 
                  variant="outline" 
                  className="mt-4"
                  onClick={() => setFilters({ priceRange: [], amenities: [], distance: [] })}
                >
                  Clear Filters
                </Button>
              </div>
            ) : (
              <div className="grid gap-6">
                {filteredHostels.map(hostel => (
                  <HostelCard 
                    key={hostel.id} 
                    hostel={hostel} 
                    onBookingClick={handleBookingClick}
                  />
                ))}
              </div>
            )}

            {/* Pagination */}
            {filteredHostels.length > 0 && (
              <div className="flex justify-center mt-12">
                <nav className="flex space-x-2">
                  <Button variant="outline" disabled>Previous</Button>
                  <Button className="bg-blue-600 hover:bg-blue-700">1</Button>
                  <Button variant="outline">2</Button>
                  <Button variant="outline">3</Button>
                  <Button variant="outline">Next</Button>
                </nav>
              </div>
            )}
          </div>
        </div>
      </div>

      <BookingModal 
        isOpen={isBookingModalOpen}
        onClose={() => setIsBookingModalOpen(false)}
        hostel={selectedHostel}
      />
    </div>
  );
}
