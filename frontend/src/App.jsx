import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LandingPage from './components/landingpage';
import LegalConsultation from './feature';
// Import other pages

const App = () => (
  <Router>
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/features" element={<LegalConsultation />} />
      {/* Define other routes */}
    </Routes>
  </Router>
);

export default App;
