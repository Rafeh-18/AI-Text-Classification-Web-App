import Layout from '../components/Layout';
import { useAuthStore } from '../store/authStore';
import Card from '../components/ui/Card';
import { User, Mail, Calendar } from 'lucide-react';

export default function Profile() {
  const { user } = useAuthStore();
  
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };
  
  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Profile</h1>
        
        <Card>
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center">
              <User className="w-8 h-8 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">{user?.username}</h2>
              <p className="text-gray-600">{user?.email}</p>
            </div>
          </div>
          
          <div className="space-y-4 pt-6 border-t border-gray-200">
            <div className="flex items-center gap-3">
              <Mail className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="font-medium text-gray-900">{user?.email}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <Calendar className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Member since</p>
                <p className="font-medium text-gray-900">{formatDate(user?.created_at)}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="w-5 h-5 text-gray-400 flex items-center justify-center">
                <div className={`w-3 h-3 rounded-full ${user?.is_active ? 'bg-green-500' : 'bg-red-500'}`} />
              </div>
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <p className="font-medium text-gray-900">
                  {user?.is_active ? 'Active' : 'Inactive'}
                </p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </Layout>
  );
}