import { Button } from "@/components/ui/button";

interface UniversityTabsProps {
  selectedUniversity: string;
  onUniversityChange: (university: string) => void;
}

export default function UniversityTabs({ selectedUniversity, onUniversityChange }: UniversityTabsProps) {
  const universities = [
    "Makerere University",
    "MUBS",
    "All Universities"
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-center space-x-4 md:space-x-8 mb-8">
        {universities.map((university) => (
          <Button
            key={university}
            variant={selectedUniversity === university ? "default" : "outline"}
            className={`px-6 py-3 font-medium transition-colors ${
              selectedUniversity === university 
                ? "bg-blue-600 text-white hover:bg-blue-700" 
                : "bg-slate-200 text-slate-700 hover:bg-slate-300"
            }`}
            onClick={() => onUniversityChange(university)}
          >
            {university}
          </Button>
        ))}
      </div>
    </div>
  );
}
