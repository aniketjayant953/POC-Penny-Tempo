import { Navigate, Route, Routes } from 'react-router-dom'
import { Sidebar } from './components/Sidebar'
import CoachPage from './pages/CoachPage'
import ManagerPage from './pages/ManagerPage'

export default function App() {
  return (
    <div className="flex h-full flex-col md:flex-row">
      <Sidebar />
      <main className="min-w-0 flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Navigate to="/coach" replace />} />
          <Route path="/coach" element={<CoachPage />} />
          <Route path="/manager" element={<ManagerPage />} />
          <Route path="*" element={<Navigate to="/coach" replace />} />
        </Routes>
      </main>
    </div>
  )
}
