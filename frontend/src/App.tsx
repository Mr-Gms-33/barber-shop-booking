import { Link, Route, Routes } from "react-router-dom";
import BookPage from "./pages/BookPage";
import StatusPage from "./pages/StatusPage";
import AdminPage from "./pages/AdminPage";

export default function App() {
  return (
    <div className="layout">
      <header>
        <h1>Barber Shop Booking</h1>
        <nav>
          <Link to="/">Book</Link>
          <Link to="/status">My booking</Link>
          <Link to="/admin">Admin</Link>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<BookPage />} />
          <Route path="/status" element={<StatusPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </main>
    </div>
  );
}
