import Navbar from "@/components/navbar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MapPin, Users, GraduationCap } from "lucide-react";
import { Link } from "wouter";

export default function Universities() {
  const universities = [
    {
      name: "Makerere University",
      description: "Uganda's oldest and most prestigious university, established in 1922. Located in Kampala with over 40,000 students.",
      location: "Makerere Hill, Kampala",
      students: "40,000+",
      hostelCount: 5,
      image: "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600",
      link: "/?university=Makerere%20University#hostels"
    },
    {
      name: "Makerere University Business School (MUBS)",
      description: "A leading business school in East Africa, established in 1997. Specializes in business, management, and accounting programs.",
      location: "Nakawa, Kampala",
      students: "15,000+",
      hostelCount: 3,
      image: "https://images.unsplash.com/photo-1562774053-701939374585?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600",
      link: "/?university=MUBS#hostels"
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-slate-900 mb-4">Universities We Serve</h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Find quality student accommodation near Uganda's top universities. We partner with trusted hostels 
            to provide safe, affordable, and convenient housing options for students.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2">
          {universities.map((university, index) => (
            <Card key={index} className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="aspect-video relative">
                <img 
                  src={university.image} 
                  alt={university.name}
                  className="w-full h-full object-cover"
                />
              </div>
              <CardHeader>
                <CardTitle className="text-2xl text-slate-900">{university.name}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-slate-600">{university.description}</p>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="flex items-center text-slate-600">
                    <MapPin className="w-5 h-5 mr-2 text-blue-600" />
                    <span className="text-sm">{university.location}</span>
                  </div>
                  <div className="flex items-center text-slate-600">
                    <Users className="w-5 h-5 mr-2 text-blue-600" />
                    <span className="text-sm">{university.students} students</span>
                  </div>
                  <div className="flex items-center text-slate-600">
                    <GraduationCap className="w-5 h-5 mr-2 text-blue-600" />
                    <span className="text-sm">{university.hostelCount} hostels</span>
                  </div>
                </div>

                <Link href={university.link}>
                  <Button className="w-full bg-blue-600 hover:bg-blue-700">
                    View Hostels Near {university.name === "Makerere University Business School (MUBS)" ? "MUBS" : university.name}
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}