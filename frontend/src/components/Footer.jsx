import React from "react";
import "../styles/footer.css";

export default function Footer() {
  return (
    <footer className="footer-mini">

      <div className="footer-video-container">
        <video
          className="footer-video"
          src="/Travel_Footer.mp4"
          autoPlay
          loop
          muted
          playsInline
        />
      </div>

      <div className="footer-overlay" />

      <div className="footer-mini-inner">
        <span className="brand">Luxura</span>
        <span className="divider">|</span>
        <span className="foot-text">© 2025 — Crafted with AI & Passion</span>
      </div>
    </footer>
  );
}