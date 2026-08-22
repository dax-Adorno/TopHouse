import { BrowserRouter, Route, Routes } from "react-router-dom";
import { SiteLayout } from "./components/SiteLayout";
import { CatalogPage } from "./pages/CatalogPage";
import { HomePage } from "./pages/HomePage";
import { PropertyDetailPage } from "./pages/PropertyDetailPage";
import "./App.css";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<SiteLayout />}>
          <Route index element={<HomePage />} />
          <Route path="propiedades" element={<CatalogPage />} />
          <Route path="propiedades/:slug" element={<PropertyDetailPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
export default App;
