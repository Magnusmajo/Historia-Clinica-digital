/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { getCurrentUser, login as loginRequest } from "../services/authService";

const AuthContext = createContext(null);

const readStoredUser = () => {
  try {
    return JSON.parse(window.localStorage.getItem("authUser") || "null");
  } catch {
    return null;
  }
};

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => window.localStorage.getItem("authToken"));
  const [user, setUser] = useState(readStoredUser);
  const [loading, setLoading] = useState(Boolean(token));

  const clearSession = () => {
    window.localStorage.removeItem("authToken");
    window.localStorage.removeItem("authUser");
    setToken(null);
    setUser(null);
    setLoading(false);
  };

  useEffect(() => {
    window.addEventListener("auth:logout", clearSession);
    return () => window.removeEventListener("auth:logout", clearSession);
  }, []);

  useEffect(() => {
    if (!token) {
      return undefined;
    }

    let mounted = true;
    getCurrentUser()
      .then((currentUser) => {
        if (!mounted) return;
        setUser(currentUser);
        window.localStorage.setItem("authUser", JSON.stringify(currentUser));
      })
      .catch(() => {
        if (mounted) clearSession();
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [token]);

  const login = async (credentials) => {
    const data = await loginRequest(credentials);
    window.localStorage.setItem("authToken", data.access_token);
    window.localStorage.setItem("authUser", JSON.stringify(data.user));
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  };

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      isAuthenticated: Boolean(token && user),
      login,
      logout: clearSession,
    }),
    [token, user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
