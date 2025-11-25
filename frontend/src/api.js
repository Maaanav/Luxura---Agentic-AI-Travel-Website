export const generatePlan = (data) =>
  fetch(`${process.env.REACT_APP_API_URL || "http://localhost:8000"}/api/generate_plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  }).then(r => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  });
