import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface FilterSidebarProps {
  filters: {
    priceRange: string[];
    amenities: string[];
    distance: string[];
  };
  onFiltersChange: (filters: any) => void;
}

export default function FilterSidebar({ filters, onFiltersChange }: FilterSidebarProps) {
  const handlePriceChange = (priceRange: string, checked: boolean) => {
    const newPriceRange = checked 
      ? [...filters.priceRange, priceRange]
      : filters.priceRange.filter(p => p !== priceRange);
    
    onFiltersChange({ ...filters, priceRange: newPriceRange });
  };

  const handleAmenityChange = (amenity: string, checked: boolean) => {
    const newAmenities = checked 
      ? [...filters.amenities, amenity]
      : filters.amenities.filter(a => a !== amenity);
    
    onFiltersChange({ ...filters, amenities: newAmenities });
  };

  const handleDistanceChange = (distance: string, checked: boolean) => {
    const newDistance = checked 
      ? [...filters.distance, distance]
      : filters.distance.filter(d => d !== distance);
    
    onFiltersChange({ ...filters, distance: newDistance });
  };

  return (
    <div className="lg:w-64 flex-shrink-0">
      <Card className="sticky top-24">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Price Range */}
          <div>
            <h4 className="font-medium text-slate-700 mb-3">Price Range (per month)</h4>
            <div className="space-y-2">
              {[
                { id: "under200", label: "Under UGX 200,000" },
                { id: "200-400", label: "UGX 200,000 - 400,000" },
                { id: "400+", label: "UGX 400,000+" }
              ].map(({ id, label }) => (
                <div key={id} className="flex items-center space-x-2">
                  <Checkbox
                    id={id}
                    checked={filters.priceRange.includes(id)}
                    onCheckedChange={(checked) => handlePriceChange(id, checked as boolean)}
                  />
                  <Label htmlFor={id} className="text-sm text-slate-600">
                    {label}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          {/* Amenities */}
          <div>
            <h4 className="font-medium text-slate-700 mb-3">Amenities</h4>
            <div className="space-y-2">
              {["WiFi", "Security", "Kitchen", "Laundry", "Parking", "Gym"].map((amenity) => (
                <div key={amenity} className="flex items-center space-x-2">
                  <Checkbox
                    id={amenity}
                    checked={filters.amenities.includes(amenity)}
                    onCheckedChange={(checked) => handleAmenityChange(amenity, checked as boolean)}
                  />
                  <Label htmlFor={amenity} className="text-sm text-slate-600">
                    {amenity}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          {/* Distance */}
          <div>
            <h4 className="font-medium text-slate-700 mb-3">Distance from University</h4>
            <div className="space-y-2">
              {[
                { id: "1km", label: "Within 1km" },
                { id: "1-3km", label: "1-3km" },
                { id: "3-5km", label: "3-5km" }
              ].map(({ id, label }) => (
                <div key={id} className="flex items-center space-x-2">
                  <Checkbox
                    id={id}
                    checked={filters.distance.includes(id)}
                    onCheckedChange={(checked) => handleDistanceChange(id, checked as boolean)}
                  />
                  <Label htmlFor={id} className="text-sm text-slate-600">
                    {label}
                  </Label>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
