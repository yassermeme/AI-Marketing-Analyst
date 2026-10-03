import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'
import { WelcomePage } from './pages/WelcomePage'

createRoot(document.getElementById('root')!).render(<StrictMode><WelcomePage /></StrictMode>)
