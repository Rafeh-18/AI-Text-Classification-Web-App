import { Clock, Trash2 } from 'lucide-react';
import Button from './ui/Button';

export default function PredictionCard({ prediction, onDelete }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-50';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };
  
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow duration-200">
      <div className="flex justify-between items-start mb-3">
        <span className="text-xs text-gray-500 flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {formatDate(prediction.created_at)}
        </span>
        {onDelete && (
          <button
            onClick={() => onDelete(prediction.id)}
            className="text-gray-400 hover:text-red-600 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>
      
      <p className="text-gray-800 font-medium mb-3 line-clamp-2">
        {prediction.input_text}
      </p>
      
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs text-gray-500">Prediction</span>
          <p className="font-semibold text-gray-900">{prediction.prediction}</p>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(prediction.confidence)}`}>
          {(prediction.confidence * 100).toFixed(1)}%
        </div>
      </div>
      
      {prediction.top_3 && prediction.top_3.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <span className="text-xs text-gray-500 mb-2 block">Top Predictions</span>
          <div className="space-y-1">
            {prediction.top_3.slice(0, 3).map((pred, idx) => (
              <div key={idx} className="flex justify-between text-sm">
                <span className="text-gray-600">{pred.label}</span>
                <span className="text-gray-800 font-medium">
                  {(pred.confidence * 100).toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}