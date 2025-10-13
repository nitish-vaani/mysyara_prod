import { ReactNode } from "react";
import { Navigate } from "react-router-dom";

interface PrivateRouteProps {
  children: ReactNode;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
    const isAuth = localStorage.getItem("isAuth");


  return isAuth ? children : <Navigate to="/sign-in" />;
};

export default PrivateRoute;
