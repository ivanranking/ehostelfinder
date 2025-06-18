import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search } from "lucide-react";
import { useLocation } from "wouter";

export default function HeroSection() {
  const [, setLocation] = useLocation();
  const [searchData, setSearchData] = useState({
    university: "",
    checkIn: "",
    roomType: "",
  });

  const handleSearch = () => {
    if (searchData.university) {
      const params = new URLSearchParams();
      params.append("university", searchData.university);
      setLocation(`/?${params.toString()}#hostels`);
    } else {
      setLocation("/#hostels");
    }
  };

  return (
    <div className="relative">
      <div className="h-96 bg-gradient-to-r from-blue-600 to-blue-700 flex items-center justify-center">
        <div className="text-center text-white max-w-4xl mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Find Your Perfect Student Accommodation
          </h1>
          <p className="text-xl mb-8 text-blue-100">
            Discover comfortable, affordable hostels near Makerere University and MUBS
          </p>
          
          {/* Search Bar */}
          <div className="bg-white rounded-xl shadow-lg p-6 max-w-4xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="relative">
                <Label htmlFor="university" className="block text-sm font-medium text-slate-700 mb-2">
                  University
                </Label>
                <Select value={searchData.university} onValueChange={(value) => setSearchData({...searchData, university: value})}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select University" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="makerere">Makerere University</SelectItem>
                    <SelectItem value="mubs">MUBS</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="relative">
                <Label htmlFor="checkin" className="block text-sm font-medium text-slate-700 mb-2">
                  Check-in
                </Label>
                <Input
                  id="checkin"
                  type="date"
                  value={searchData.checkIn}
                  onChange={(e) => setSearchData({...searchData, checkIn: e.target.value})}
                  className="w-full"
                />
              </div>
              
              <div className="relative">
                <Label htmlFor="roomtype" className="block text-sm font-medium text-slate-700 mb-2">
                  Room Type
                </Label>
                <Select value={searchData.roomType} onValueChange={(value) => setSearchData({...searchData, roomType: value})}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Any" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="single">Single Room</SelectItem>
                    <SelectItem value="shared">Shared Room</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex items-end">
                <Button 
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                  onClick={handleSearch}
                >
                  <Search className="w-4 h-4 mr-2" />
                  Search
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
