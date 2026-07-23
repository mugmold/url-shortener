import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import TooManyRequests from './pages/TooManyRequests';
import NotFound from './pages/NotFound';
import RedirectHandler from './pages/RedirectHandler';

function App() {
  return (
    <Routes>
      <Route path="/too-many-requests" element={<TooManyRequests />} />

      <Route
        path="/*"
        element={
          <div className="min-h-screen flex flex-col">
            <Navbar />
            <main className="flex-1">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings"
                  element={
                    <ProtectedRoute>
                      <Settings />
                    </ProtectedRoute>
                  }
                />

                <Route path="/not-found" element={<NotFound />} />

                <Route path="/:shortCode" element={<RedirectHandler />} />

                <Route path="*" element={<NotFound />} />
              </Routes>
            </main>
          </div>
        }
      />
    </Routes>
  );
}

export default App;