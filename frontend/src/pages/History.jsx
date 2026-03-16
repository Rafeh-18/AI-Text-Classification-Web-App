import { useState, useEffect } from 'react';
import { predictAPI } from '../services/api';
import toast from 'react-hot-toast';
import Layout from '../components/Layout';
import Card from '../components/ui/Card';
import PredictionCard from '../components/PredictionCard';
import Loading from '../components/ui/Loading';
import { History as HistoryIcon } from 'lucide-react'; // Fixed: removed unused `Trash2` import

export default function History() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await predictAPI.getHistory({ limit: 50, offset: 0 });
      setPredictions(response.data.predictions);
      setTotal(response.data.total);
    } catch (error) {
      toast.error('Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this prediction?')) return;

    try {
      await predictAPI.deletePrediction(id);
      setPredictions(prev => prev.filter(p => p.id !== id));
      setTotal(prev => prev - 1);
      toast.success('Prediction deleted');
    } catch (error) {
      toast.error('Failed to delete prediction');
    }
  };

  if (loading) {
    return (
      <Layout>
        <Loading />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Prediction History</h1>
            <p className="text-gray-600 mt-2">View all your past classifications</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-primary-600">{total}</p>
            <p className="text-sm text-gray-500">Total predictions</p>
          </div>
        </div>

        {/* Predictions List */}
        {predictions.length === 0 ? (
          <Card className="text-center py-12">
            <HistoryIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900">No predictions yet</h3>
            <p className="text-gray-600 mt-2">Start classifying text to see your history here</p>
          </Card>
        ) : (
          <div className="grid gap-4">
            {predictions.map((prediction) => (
              <PredictionCard
                key={prediction.id}
                prediction={prediction}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}