import React from "react";

const aliasMap = {
  travel_flight: "/Travel_Flight.mp4",
  travel_flights: "/Travel_Flight.mp4",
  flights: "/Travel_Flight.mp4",
  flight: "/Travel_Flight.mp4",

  travel_footer: "/Travel_Footer.mp4",
  footer: "/Travel_Footer.mp4",

  travel_result: "/Travel_Result.mp4",
  result: "/Travel_Result.mp4",
  itinerary: "/Travel_Result.mp4",

  travel_info: "/Travel_Info.mp4",
  info: "/Travel_Info.mp4",

  travel_home: "/Travel_Home.mp4",
  home: "/Travel_Home.mp4",
  transport: "/Travel_Home.mp4",
  weather: "/Travel_Home.mp4",

  travel_input: "/Travel_Input.mp4",
  input: "/Travel_Input.mp4",

  travel_loading: "/Travel_Loading.mp4",
  loading: "/Travel_Loading.mp4",

  default: "/Travel_Flight.mp4",
};

function normalizeKey(key) {
  if (!key || typeof key !== "string") return "default";
  return key.replace(/[^a-z0-9]/gi, "_").toLowerCase();
}

export default function VideoBackground({ video = "default", poster }) {
  const key = normalizeKey(video);
  const src = aliasMap[key] || aliasMap.default || video;

  return (
    <div className="video-bg" aria-hidden="true">
      <div className="bg-poster" aria-hidden="true" />
      <video
        className="bg-video"
        autoPlay
        loop
        muted
        playsInline
        preload="auto"
        poster={poster || undefined}
      >
        <source src={src} type="video/mp4" />
      </video>

      <div className="video-overlay" aria-hidden="true" />
    </div>
  );
}