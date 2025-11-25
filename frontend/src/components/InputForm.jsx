import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import VideoBackground from "./VideoBackground";
import LoadingCompass from "./LoadingCompass";
import "../styles/input-form.css";

const INDIAN_CITIES = [
  { name: "Agra", code: "AGR" },
  { name: "Ahmedabad", code: "AMD" },
  { name: "Aizawl", code: "AJL" },
  { name: "Amritsar", code: "ATQ" },
  { name: "Ayodhya", code: "AYJ" },
  { name: "Bengaluru", code: "BLR" },
  { name: "Bhopal", code: "BHO" },
  { name: "Bhubaneswar", code: "BBI" },
  { name: "Chandigarh", code: "IXC" },
  { name: "Chennai", code: "MAA" },
  { name: "Coimbatore", code: "CJB" },
  { name: "Delhi", code: "DEL" },
  { name: "Goa (Dabolim)", code: "GOI" },
  { name: "Goa (Mopa)", code: "GOX" },
  { name: "Guwahati", code: "GAU" },
  { name: "Gwalior", code: "GWL" },
  { name: "Hyderabad", code: "HYD" },
  { name: "Imphal", code: "IMF" },
  { name: "Indore", code: "IDR" },
  { name: "Jaisalmer", code: "JSA" },
  { name: "Jaipur", code: "JAI" },
  { name: "Jammu", code: "IXJ" },
  { name: "Jodhpur", code: "JDH" },
  { name: "Kanpur", code: "KNU" },
  { name: "Kannur", code: "CNN" },
  { name: "Kochi", code: "COK" },
  { name: "Kolkata", code: "CCU" },
  { name: "Kozhikode", code: "CCJ" },
  { name: "Leh", code: "IXL" },
  { name: "Lucknow", code: "LKO" },
  { name: "Madurai", code: "IXM" },
  { name: "Mangalore", code: "IXE" },
  { name: "Mumbai", code: "BOM" },
  { name: "Mysore", code: "MYQ" },
  { name: "Nagpur", code: "NAG" },
  { name: "Patna", code: "PAT" },
  { name: "Port Blair", code: "IXZ" },
  { name: "Pune", code: "PNQ" },
  { name: "Raipur", code: "RPR" },
  { name: "Rajkot", code: "RAJ" },
  { name: "Ranchi", code: "IXR" },
  { name: "Shillong", code: "SHL" },
  { name: "Srinagar", code: "SXR" },
  { name: "Surat", code: "STV" },
  { name: "Thiruvananthapuram", code: "TRV" },
  { name: "Tiruchirappalli", code: "TRZ" },
  { name: "Udaipur", code: "UDR" },
  { name: "Vadodara", code: "BDQ" },
  { name: "Varanasi", code: "VNS" },
  { name: "Visakhapatnam", code: "VTZ" }
].sort((a, b) => a.name.localeCompare(b.name));

const THEMES = [
  "Hill Stations",
  "Beaches & Islands",
  "Heritage & Culture",
  "Pilgrimage & Spiritual",
  "Adventure & Trekking",
  "Wildlife & Nature",
  "Desert",
  "Family-Friendly",
];

export default function InputForm() {
  const [form, setForm] = useState({
    source: "BOM",
    destination: "DEL",
    theme: "Luxury",
    depart_date: "",
    return_date: "",
    trip_type: "tourist",
  });
  const [showLoading, setShowLoading] = useState(false);
  const navigate = useNavigate();

  const today = new Date();
  const todayStr = today.toISOString().split("T")[0];


  useEffect(() => {
    if (!form.depart_date) return;
    const departDate = new Date(form.depart_date);
    const minReturnDate = new Date(departDate.getTime() + 24 * 60 * 60 * 1000);
    const minReturnStr = minReturnDate.toISOString().split("T")[0];
    const prevReturn = form.return_date ? new Date(form.return_date) : null;
    if (!form.return_date) {
      setForm((p) => ({ ...p, return_date: minReturnStr }));
      return;
    }
    if (prevReturn && prevReturn < minReturnDate) {
      setForm((p) => ({ ...p, return_date: minReturnStr }));
      return;
    }
  }, [form.depart_date]);

  const tripDays =
    form.depart_date && form.return_date
      ? Math.max(
          1,
          Math.ceil(
            (new Date(form.return_date) - new Date(form.depart_date)) /
              (1000 * 60 * 60 * 24)
          )
        )
      : 0;

  const handleSubmit = () => {
    if (!form.depart_date || !form.return_date) {
      alert("Please select both departure and return dates");
      return;
    }
    if (new Date(form.return_date) <= new Date(form.depart_date)) {
      alert("Return date must be after departure date");
      return;
    }
    if (form.source === form.destination) {
      alert("Source and destination cannot be the same");
      return;
    }

    setShowLoading(true);

    const params = new URLSearchParams({
      source: form.source,
      destination: form.destination,
      theme: form.theme,
      depart_date: form.depart_date,
      return_date: form.return_date,
      num_days: String(tripDays),
      trip_type: form.trip_type,
    });

    setTimeout(() => {
      navigate(`/results?${params.toString()}`);
      setShowLoading(false);
    }, 700);
  };

  const handleSwap = () => {
    setForm((p) => ({ ...p, source: p.destination, destination: p.source }));
  };

  const handleReset = () => {
    setForm({
      source: "BOM",
      destination: "DEL",
      theme: "Luxury",
      depart_date: "",
      return_date: "",
      trip_type: "tourist",
    });
  };

  if (showLoading) return <LoadingCompass />;

  return (
    <section className="input-section" aria-label="Plan your escape">
      <VideoBackground video="Input" />

      <div className="content input-form-block" role="form" aria-labelledby="plan-your-escape">
        <h2 id="plan-your-escape" className="form-heading">Plan Your Escape</h2>

        <div className="form-row">
          <div className="input-group small">
            <label htmlFor="source-select">From</label>
            <select
              id="source-select"
              value={form.source}
              onChange={(e) => setForm({ ...form, source: e.target.value })}
            >
              {INDIAN_CITIES.map((city) => (
                <option key={city.code} value={city.code}>
                  {city.name} ({city.code})
                </option>
              ))}
            </select>
          </div>

          <button
            type="button"
            aria-label="Swap from and to"
            className="swap-btn"
            onClick={handleSwap}
            title="Swap"
          >
            ⇄
          </button>

          <div className="input-group small">
            <label htmlFor="destination-select">To</label>
            <select
              id="destination-select"
              value={form.destination}
              onChange={(e) => setForm({ ...form, destination: e.target.value })}
            >
              {INDIAN_CITIES.map((city) => (
                <option key={city.code} value={city.code}>
                  {city.name} ({city.code})
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="input-group small">
            <label htmlFor="depart-date">Departure</label>
            <input
              id="depart-date"
              type="date"
              value={form.depart_date}
              min={todayStr}
              onChange={(e) => setForm({ ...form, depart_date: e.target.value })}
            />
          </div>

          <div className="input-group small">
            <label htmlFor="return-date">Return</label>
            <input
              id="return-date"
              type="date"
              value={form.return_date}
              min={form.depart_date || todayStr}
              onChange={(e) => setForm({ ...form, return_date: e.target.value })}
            />
          </div>
        </div>

        <div className="form-row">
          <div className="input-group small">
            <label htmlFor="theme-select">Theme</label>
            <select
              id="theme-select"
              value={form.theme}
              onChange={(e) => setForm({ ...form, theme: e.target.value })}
            >
              {THEMES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div className="input-group small">
            <label htmlFor="trip-days">Your Trip</label>
            <input
              id="trip-days"
              type="text"
              value={tripDays > 0 ? `${tripDays} ${tripDays === 1 ? "day" : "days"}` : ""}
              readOnly
              aria-readonly="true"
              placeholder="Trip length will appear here"
              className="trip-pill"
            />
          </div>
        </div>

        <div className="form-actions">
          <button onClick={handleSubmit} className="cta-button" aria-label="Generate trip">
            Generate My Luxury Trip
          </button>

          <button onClick={handleReset} className="reset-btn" aria-label="Reset form">
            Reset
          </button>
        </div>
      </div>
    </section>
  );
}