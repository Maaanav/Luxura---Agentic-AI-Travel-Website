import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import "../styles/results.css";
import VideoBackground from "../components/VideoBackground";
import LoadingCompass from "../components/LoadingCompass";
import { generatePlan } from "../api";

function safeGet(obj, path, fallback = undefined) {
  try {
    const parts = path.split(".");
    let cur = obj;
    for (let p of parts) {
      if (!cur) return fallback;
      cur = cur[p];
    }
    return cur === undefined ? fallback : cur;
  } catch {
    return fallback;
  }
}

export default function Results() {
  const [searchParams] = useSearchParams();
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const payload = Object.fromEntries(searchParams.entries());
    if (payload.num_days) payload.num_days = Number(payload.num_days);

    generatePlan(payload)
      .then((raw) => {
        const normalized = {
          source: safeGet(raw, "source", payload.source),
          destination: safeGet(raw, "destination", payload.destination),
          flights: safeGet(raw, "flights", []),
          hotels: safeGet(raw, "hotels", { luxury: [], mid_range: [], budget: [] }),
          itinerary: safeGet(raw, "itinerary", []),
          attractions: safeGet(raw, "attractions", []),
          restaurants: safeGet(raw, "restaurants", []),
          transport: safeGet(raw, "transport", {}),
          weather: safeGet(raw, "weather", {}),
        };

        normalized.flights = (normalized.flights || []).map((f) => ({
          airline: f.airline || f.name || "Unknown",
          price: f.price || "N/A",
          duration: f.duration || f.duration_text || "N/A",
          stops: f.stops || f.total_layovers || "N/A",
          airline_logo: f.airline_logo || f.airline_logo_url || null,
          raw: f,
        }));

        setPlan(normalized);
      })
      .catch((e) => {
        console.error("Failed to load plan:", e);
        setError("Failed to load plan.");
      })
      .finally(() => setLoading(false));
  }, [searchParams]);

  if (loading) return <LoadingCompass />;

  if (error) {
    return (
      <div className="results-page">
        <VideoBackground video="Travel_Result" />
        <div className="lux-card error-card">{error}</div>
      </div>
    );
  }

  if (!plan) return null;

  const uploadedFallback = "";
  const publicFallback = "/logos/default.png";

  return (
    <div className="results-page">

      {/* ========================= 1) FLIGHTS  ========================= */}
      <section className="lux-section">
        <VideoBackground video="Travel_Flights" />
        <div className="lux-card">
          <h2 className="lux-title">Flights</h2>
          <p className="lux-sub">Live-sourced flight options — curated for you</p>

          <div className="flights-grid">
            {plan.flights.length === 0 && <div className="lux-empty">No flights found</div>}

            {plan.flights.map((f, idx) => (
              <div className="flight-card" key={`flight-${idx}`} role="article" aria-label={`flight ${f.airline}`}>
                <img
                  className="flight-logo"
                  src={f.airline_logo || uploadedFallback}
                  alt={f.airline}
                  onError={(e) => {
                    const firstFallback = uploadedFallback;
                    const finalFallback = publicFallback;
                    try {
                      if (e.currentTarget.src !== firstFallback) {
                        e.currentTarget.src = firstFallback;
                      } else if (e.currentTarget.src !== finalFallback) {
                        e.currentTarget.src = finalFallback;
                      }
                    } catch {
                      e.currentTarget.src = finalFallback;
                    }
                  }}
                />

                <div className="flight-info">
                  <div className="flight-airline">{f.airline}</div>
                  <div className="flight-meta">{f.duration} • {f.stops}</div>
                </div>

                <div className="flight-price">{f.price}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========================= 2) HOTELS  ========================= */}
      <section className="lux-section image-section">
        <div className="image-bg" style={{ backgroundImage: 'url("/Travel_Hotel.png")' }} />
        <div className="lux-card">
          <h2 className="lux-title">Hotels</h2>
          <p className="lux-sub">Hand-picked stays for every category</p>

          {["luxury", "mid_range", "budget"].map((tier) => (
            <div className="hotel-tier" key={tier}>
              <h3 className="tier-label">
                {tier === "luxury" ? "Luxury" : tier === "mid_range" ? "Mid-range" : "Budget"}
              </h3>

              <div className="hotels-grid">
                {plan.hotels[tier]?.length === 0 && <div className="lux-empty small">No hotels found</div>}

                {plan.hotels[tier]?.map((h, i) => (
                  <div className="hotel-card" key={`${tier}-${i}`}>
                    <div className="hotel-main">
                      <div className="hotel-name">{h.name}</div>
                      <div className="hotel-area">{h.area || h.location}</div>
                    </div>
                    <div className="hotel-price">{h.price || "N/A"}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ========================= 3) ITINERARY ========================= */}
      <section className="lux-section">
        <VideoBackground video="Travel_Result" />
        <div className="lux-card">
          <h2 className="lux-title">Itinerary</h2>
          <p className="lux-sub">Daily personalized plan</p>

          <div className="it-list">
            {plan.itinerary.map((day, i) => (
              <div className="day-item" key={`day-${i}`}>
                <div className="day-num">Day {day.day || i + 1}</div>
                <div className="day-body">
                  <p><strong>Morning:</strong> {day.morning}</p>
                  <p><strong>Afternoon:</strong> {day.afternoon}</p>
                  <p><strong>Evening:</strong> {day.evening}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========================= 4) ATTRACTIONS and RESTAURANTS ========================= */}
      <section className="lux-section image-section">
        <div className="image-bg" style={{ backgroundImage: 'url("/Travel_Attraction.png")' }} />
        <div className="lux-card">
          <h2 className="lux-title">Attractions</h2>
          <p className="lux-sub">Top sights to visit</p>

          <div className="two-col-list">
            {plan.attractions.length === 0 && <div className="lux-empty">No attractions available</div>}
            {plan.attractions.map((a, i) => (
              <div className="ar-card" key={`a-${i}`}>
                <div className="ar-name">{a.name}</div>
                <div className="ar-meta">{a.why}</div>
                <div className="ar-meta small">Best time: {a.best_time || "Anytime"}</div>
              </div>
            ))}
          </div>

          <hr className="section-divider" />

          <h2 className="lux-title small-title">Restaurants</h2>
          <p className="lux-sub">Recommended places to eat</p>

          <div className="two-col-list">
            {plan.restaurants.length === 0 && <div className="lux-empty">No restaurants available</div>}
            {plan.restaurants.map((r, i) => (
              <div className="ar-card" key={`r-${i}`}>
                <div className="ar-name">{r.name}</div>
                <div className="ar-meta">{r.cuisine}</div>
                {r.must_try && <div className="ar-meta small">Must try: {Array.isArray(r.must_try) ? r.must_try.join(", ") : r.must_try}</div>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========================= 5) TRANSPORT + WEATHER ========================= */}
      <section className="lux-section">
        <VideoBackground video="Travel_Home" />
        <div className="lux-card grid-2">
          <div>
            <h3 className="tier-label">Transport</h3>
            <p className="lux-text">{plan.transport.best_way || "Local transit details unavailable"}</p>
            <p className="lux-text">Cost: {plan.transport.avg_cost || "Varies"}</p>
            {plan.transport.tips && <p className="lux-text small">Tips: {plan.transport.tips}</p>}
          </div>

          <div>
            <h3 className="tier-label">Weather</h3>
            <p className="lux-text">{plan.weather.summary || "Weather data unavailable"}</p>
            {plan.weather.temperature && <p className="lux-text"><strong>Forecast:</strong> {plan.weather.temperature}</p>}
            {plan.weather.recommendation && <p className="lux-text small">{plan.weather.recommendation}</p>}
          </div>
        </div>
      </section>
    </div>
  );
}