import React from "react";
import VideoBackground from "./VideoBackground";
import "../styles/hero.css";

export default function Hero() {
  return (
    <section className="hero-section">
      <VideoBackground video="Home" />

      <div className="content">
        <div className="hero-tag">AI · LUXURY · PERSONALIZED</div>

        <h1 className="hero-title">Travel Reimagined</h1>


        <div className="hero-ctas">
          <button className="hero-cta-primary">
            Plan My Trip
          </button>

          <button className="hero-cta-ghost">
            Learn More
          </button>
        </div>
      </div>
    </section>
  );
}
