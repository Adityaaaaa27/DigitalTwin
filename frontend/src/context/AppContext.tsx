import {
  createContext,
  useContext,
  useState,
  ReactNode,
  useCallback,
  useEffect,
} from "react";
import { PredictionResult, AuthUser } from "@/services/api";

const PREDICTION_KEY = "dt_prediction_result";
const AUTH_KEY = "dt_auth_user";

function loadPrediction(): PredictionResult | null {
  try {
    const raw = localStorage.getItem(PREDICTION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function loadAuthUser(): AuthUser | null {
  try {
    const raw = localStorage.getItem(AUTH_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

interface AppState {
  // Auth
  user: AuthUser | null;
  isAuthenticated: boolean;
  loginUser: (user: AuthUser) => void;
  logoutUser: () => void;

  // Data
  userId: string;
  predictionResult: PredictionResult | null;
  setPredictionResult: (r: PredictionResult | null) => void;
}

const AppContext = createContext<AppState | null>(null);

export const AppProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<AuthUser | null>(loadAuthUser);
  const [predictionResult, _setPredictionResult] =
    useState<PredictionResult | null>(loadPrediction);

  const isAuthenticated = user !== null;
  const userId = user ? String(user.id) : "";

  const loginUser = useCallback((u: AuthUser) => {
    setUser(u);
    localStorage.setItem(AUTH_KEY, JSON.stringify(u));
    // Clear any stale prediction data from other users
    _setPredictionResult(null);
    localStorage.removeItem(PREDICTION_KEY);
  }, []);

  const logoutUser = useCallback(() => {
    setUser(null);
    _setPredictionResult(null);
    localStorage.removeItem(AUTH_KEY);
    localStorage.removeItem(PREDICTION_KEY);
  }, []);

  const setPredictionResult = useCallback((r: PredictionResult | null) => {
    _setPredictionResult(r);
    if (r) {
      localStorage.setItem(PREDICTION_KEY, JSON.stringify(r));
    } else {
      localStorage.removeItem(PREDICTION_KEY);
    }
  }, []);

  return (
    <AppContext.Provider
      value={{
        user,
        isAuthenticated,
        loginUser,
        logoutUser,
        userId,
        predictionResult,
        setPredictionResult,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useAppState = () => {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppState must be within AppProvider");
  return ctx;
};
