import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import Button from '../components/ui/Button';
import { Sparkles, Shield, History, Zap } from 'lucide-react';

export default function Home() {
  const { isAuthenticated } = useAuthStore();
  
  const features = [
    {
      icon: Sparkles,
      title: 'AI-Powered',
      description: 'Advanced machine learning models for accurate text classification'
    },
    {
      icon: Shield,
      title: 'Secure',
      description: 'JWT authentication keeps your data safe and private'
    },
    {
      icon: History,
      title: 'History Tracking',
      description: 'Keep track of all your predictions with full history'
    },
    {
      icon: Zap,
      title: 'Fast',
      description: 'Real-time predictions with optimized backend'
    }
  ];
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-100">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white/80 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">AI</span>
            </div>
            <span className="text-xl font-bold text-gray-900">Text Classifier</span>
          </div>
          <div className="flex gap-4">
            {isAuthenticated ? (
              <Link to="/dashboard">
                <Button>Dashboard</Button>
              </Link>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="secondary">Sign In</Button>
                </Link>
                <Link to="/register">
                  <Button>Get Started</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </header>
      
      {/* Hero */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            AI-Powered Text Classification
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Classify text into 22 different categories with state-of-the-art machine learning.
            Fast, accurate, and secure.
          </p>
          <div className="flex gap-4 justify-center">
            {isAuthenticated ? (
              <Link to="/dashboard">
                <Button className="px-8 py-3 text-lg">Go to Dashboard</Button>
              </Link>
            ) : (
              <Link to="/register">
                <Button className="px-8 py-3 text-lg">Start Free</Button>
              </Link>
            )}
          </div>
        </div>
      </section>
      
      {/* Features */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Why Choose Our Platform?
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <div key={idx} className="text-center">
                  <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <Icon className="w-6 h-6 text-primary-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="py-8 px-4 border-t border-gray-200">
        <div className="max-w-7xl mx-auto text-center text-gray-600">
          <p>© 2024 AI Text Classifier. Built with FastAPI + React.</p>
        </div>
      </footer>
    </div>
  );
}