import { useState } from "react";
import { api } from "../api";

type Booking = {
  booking_code: string;
  status: string;
  start_at: string;
  service_name: string;
  barber_name: string | null;
};

export default function StatusPage() {
  const [code, setCode] = useState("");
  const [last4, setLast4] = useState("");
  const [booking, setBooking] = useState<Booking | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function lookup(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const b = await api<Booking>("/api/bookings/lookup", {
        method: "POST",
        body: JSON.stringify({ booking_code: code, phone_last4: last4 }),
      });
      setBooking(b);
    } catch {
      setError("Booking not found or verification failed");
      setBooking(null);
    }
  }

  async function cancel() {
    if (!booking) return;
    await api(`/api/bookings/${booking.booking_code}/cancel`, {
      method: "POST",
      body: JSON.stringify({ booking_code: code, phone_last4: last4 }),
    });
    const b = await api<Booking>("/api/bookings/lookup", {
      method: "POST",
      body: JSON.stringify({ booking_code: code, phone_last4: last4 }),
    });
    setBooking(b);
  }

  return (
    <div className="card">
      <h2>My booking</h2>
      <form onSubmit={lookup}>
        <label>
          Booking code
          <input value={code} onChange={(e) => setCode(e.target.value.toUpperCase())} required />
        </label>
        <label>
          Last 4 digits of phone
          <input value={last4} onChange={(e) => setLast4(e.target.value)} maxLength={4} required />
        </label>
        <button type="submit">View status</button>
      </form>
      {error && <p className="error">{error}</p>}
      {booking && (
        <div>
          <p>
            Status: <strong>{booking.status}</strong>
          </p>
          <p>
            {booking.service_name} — {new Date(booking.start_at).toLocaleString()}
          </p>
          {booking.barber_name && <p>Barber: {booking.barber_name}</p>}
          {(booking.status === "pending" || booking.status === "confirmed") && (
            <button type="button" onClick={cancel}>
              Cancel booking
            </button>
          )}
        </div>
      )}
    </div>
  );
}
