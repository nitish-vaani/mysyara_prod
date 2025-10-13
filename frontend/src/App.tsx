// import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// import Home from "./pages/home";
// import History from './pages/history'
// import SignIn from "./pages/sign-in";
// import PrivateRoute from "./components/private-route";
// import { pagePaths } from "./common/constants";
// import './App.css'
// import Header from "./components/header";
// import Feedback from './pages/feedback'
// import Footer from "./components/footer";

// const App = () => {
//   return (
//     <Router>
//       <Routes>
//         <Route path={pagePaths.signin} element={<SignIn />} />
//         <Route
//           path={pagePaths.landing}
//           element={
//             <PrivateRoute>
//               <Header/>
//               <Home />
//               <Footer/>
//             </PrivateRoute>
//           }
//         />
//         <Route
//           path={pagePaths.home}
//           element={
//             <PrivateRoute>
//               <Header/>
//               <Home />
//               <Footer/>
//             </PrivateRoute>
//           }
//         />
//         <Route
//           path={pagePaths.history}
//           element={
//             <PrivateRoute>
//                <Header/>
//               <History />
//               <Footer/>
//             </PrivateRoute>
//           }
//         />
//         <Route
//           path={pagePaths.feedback}
//           element={
//             <PrivateRoute>
//                <Header/>
//               <Feedback />
//               <Footer/>
//             </PrivateRoute>
//           }
//         />
//       </Routes>
//     </Router>
//   );
// };

// export default App;


import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/home";
import History from './pages/history'
import SignIn from "./pages/sign-in";
import Dashboard from "./pages/dashboard";
import PrivateRoute from "./components/private-route";
import { pagePaths } from "./common/constants";
import './App.css'
import Header from "./components/header";
import Feedback from './pages/feedback'
import Footer from "./components/footer";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path={pagePaths.signin} element={<SignIn />} />
        <Route
          path={pagePaths.landing}
          element={
            <PrivateRoute>
              <Header/>
              <Home />
              <Footer/>
            </PrivateRoute>
          }
        />
        <Route
          path={pagePaths.home}
          element={
            <PrivateRoute>
              <Header/>
              <Home />
              <Footer/>
            </PrivateRoute>
          }
        />
        <Route
          path={pagePaths.dashboard}
          element={
            <PrivateRoute>
              <Header/>
              <Dashboard />
              <Footer/>
            </PrivateRoute>
          }
        />
        <Route
          path={pagePaths.history}
          element={
            <PrivateRoute>
               <Header/>
              <History />
              <Footer/>
            </PrivateRoute>
          }
        />
        <Route
          path={pagePaths.feedback}
          element={
            <PrivateRoute>
               <Header/>
              <Feedback />
              <Footer/>
            </PrivateRoute>
          }
        />
      </Routes>
    </Router>
  );
};

export default App;

