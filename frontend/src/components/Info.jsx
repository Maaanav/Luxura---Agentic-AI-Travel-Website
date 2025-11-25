import React from "react";
import VideoBackground from "./VideoBackground";

export default function Info() {
  return (
    <section className="info-section">
      <VideoBackground video="Info" />

      <div className="content right info-text-block">
        <h2>Travel Reimagined</h2>
        <p>
          Discover journeys crafted with precision — powered by real airline data, 
          live weather intelligence, and AI-driven personalization. 
          From serene beach escapes to luxurious hill retreats, 
          Luxura delivers a seamless travel-planning experience built for modern explorers.
        </p>

        <p>
          Let our intelligent agents curate flights, hotels, attractions, and 
          customized itineraries so you can focus on what matters — the journey itself.
        </p>

        <ul className="info-highlights">
          <li>◎ Real-time flight insights</li>
          <li>◎ Handpicked luxury stays</li>
          <li>◎ AI-tailored day-by-day itinerary</li>
          <li>◎ Weather-aware recommendations</li>
          <li>◎ Beautiful visual experience</li>
        </ul>
      </div>
    </section>
  );
}
