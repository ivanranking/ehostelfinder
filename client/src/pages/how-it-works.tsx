import Navbar from "@/components/navbar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Search, Eye, Calendar, CheckCircle } from "lucide-react";
import { Link } from "wouter";

export default function HowItWorks() {
  const steps = [
    {
      icon: <Search className="w-12 h-12 text-blue-600" />,
      title: "Search & Filter",
      description: "Browse available hostels near your university. Use our filters to find accommodation that matches your budget, preferred amenities, and distance requirements.",
      details: ["Filter by price range", "Select preferred amenities", "Choose distance from university", "Compare multiple options"]
    },
    {
      icon: <Eye className="w-12 h-12 text-blue-600" />,
      title: "View Details",
      description: "Explore detailed information about each hostel including photos, amenities, contact information, and reviews from other students.",
      details: ["High-quality photos", "Detailed amenity lists", "Student reviews and ratings", "Contact information"]
    },
    {
      icon: <Calendar className="w-12 h-12 text-blue-600" />,
      title: "Book Your Room",
      description: "Submit your booking request with your preferred move-in date and room type. Fill out the simple booking form with your details.",
      details: ["Choose move-in date", "Select room type", "Provide student information", "Add special requests"]
    },
    {
      icon: <CheckCircle className="w-12 h-12 text-blue-600" />,
      title: "Get Confirmed",
      description: "The hostel will contact you directly to confirm your booking and provide payment instructions. Move in on your scheduled date.",
      details: ["Direct hostel contact", "Payment confirmation", "Move-in coordination", "24/7 support available"]
    }
  ];

  const benefits = [
    {
      title: "Verified Hostels",
      description: "All hostels are verified for safety, cleanliness, and student-friendly policies."
    },
    {
      title: "Student Reviews",
      description: "Read honest reviews from fellow students who have stayed at these hostels."
    },
    {
      title: "Best Prices",
      description: "Compare prices across multiple hostels to find the best deal for your budget."
    },
    {
      title: "University Proximity",
      description: "All listings show exact distance from your university campus."
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-slate-900 mb-4">How E-Hostel Works</h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Finding student accommodation has never been easier. Follow these simple steps to secure your perfect hostel room.
          </p>
        </div>

        {/* Steps */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-slate-900 text-center mb-12">Simple 4-Step Process</h2>
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            {steps.map((step, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="mx-auto mb-4 p-4 bg-blue-50 rounded-full w-fit">
                    {step.icon}
                  </div>
                  <CardTitle className="text-xl">
                    <span className="text-blue-600 font-bold">Step {index + 1}:</span> {step.title}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-slate-600">{step.description}</p>
                  <ul className="text-sm text-slate-500 space-y-1">
                    {step.details.map((detail, idx) => (
                      <li key={idx} className="flex items-center">
                        <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mr-2"></div>
                        {detail}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Benefits */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-slate-900 text-center mb-12">Why Choose E-Hostel?</h2>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {benefits.map((benefit, index) => (
              <Card key={index} className="text-center p-6">
                <CardContent className="pt-0">
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">{benefit.title}</h3>
                  <p className="text-slate-600 text-sm">{benefit.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="bg-blue-600 rounded-2xl p-8 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">Ready to Find Your Perfect Hostel?</h2>
          <p className="text-xl mb-6 text-blue-100">
            Join thousands of students who have found their ideal accommodation through E-Hostel.
          </p>
          <Link href="/">
            <Button size="lg" className="bg-white text-blue-600 hover:bg-slate-100">
              Start Browsing Hostels
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}