import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { predictAPI } from '../services/api';
import toast from 'react-hot-toast';
import Layout from '../components/Layout';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import PredictionCard from '../components/PredictionCard';
import { Sparkles, Send, Zap } from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [recentPredictions, setRecentPredictions] = useState([]);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!text.trim()) {
      toast.error('Please enter some text');
      return;
    }
    
    if (text.trim().length < 5) {
      toast.error('Text must be at least 5 characters');
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await predictAPI.classify(text.trim());
      setResult(response.data);
      
      // Add to recent predictions
      setRecentPredictions(prev => [response.data, ...prev].slice(0, 5));
      
      toast.success('Classification complete!');
      setText('');
    } catch (error) {
      const message = error.response?.data?.detail || 'Classification failed';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">Classify text using AI</p>
        </div>
        
        {/* Classification Form */}
        <Card className="mb-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Enter text to classify
              </label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Type or paste your text here..."
                rows={5}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none"
              />
              <p className="text-sm text-gray-500 mt-2">
                {text.length} characters (min: 5, max: 10000)
              </p>
            </div>
            
            <Button type="submit" loading={loading} className="w-full">
              <Sparkles className="w-4 h-4" />
              Classify Text
            </Button>
          </form>
        </Card>
        
        {/* Result */}
        {result && (
          <Card className="mb-8 border-primary-200 bg-primary-50">
            <div className="flex items-center gap-3 mb-4">
              <Zap className="w-6 h-6 text-primary-600" />
              <h2 className="text-lg font-semibold text-gray-900">Classification Result</h2>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <span className="text-sm text-gray-500">Prediction</span>
                <p className="text-xl font-bold text-gray-900">{result.prediction}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Confidence</span>
                <p className={`text-xl font-bold ${
                  result.confidence >= 0.8 ? 'text-green-600' :
                  result.confidence >= 0.6 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {(result.confidence * 100).toFixed(1)}%
                </p>
              </div>
            </div>
            
            {result.top_3 && (
              <div className="mt-6 pt-6 border-t border-primary-200">
                <span className="text-sm text-gray-500 mb-3 block">All Predictions</span>
                <div className="space-y-2">
                  {result.top_3.map((pred, idx) => (
                    <div key={idx} className="flex justify-between items-center">
                      <span className="text-gray-700">{pred.label}</span>
                      <div className="flex items-center gap-3">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-primary-600 h-2 rounded-full" 
                            style={{ width: `${pred.confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-gray-900 w-12 text-right">
                          {(pred.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        )}
        
        {/* Quick Stats */}
        <div className="grid md:grid-cols-3 gap-4 mb-8">
          <Card className="text-center">
            <p className="text-3xl font-bold text-primary-600">22</p>
            <p className="text-gray-600">Classes</p>
          </Card>
          <Card className="text-center">
            <p className="text-3xl font-bold text-green-600">89%</p>
            <p className="text-gray-600">Accuracy</p>
          </Card>
          <Card className="text-center">
            <button 
              onClick={() => navigate('/history')}
              className="text-3xl font-bold text-primary-600 hover:underline"
            >
              View All →
            </button>
            <p className="text-gray-600">History</p>
          </Card>
        </div>
      </div>
    </Layout>
  );
}