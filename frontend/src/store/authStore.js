import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      login: (user, token) => {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
        set({ user, token, isAuthenticated: true });
      },
      
      logout: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        set({ user: null, token: null, isAuthenticated: false });
      },
      
      setUser: (user) => set({ user }),
      
      initialize: () => {
        const token = localStorage.getItem('token');
        const user = localStorage.getItem('user');
        if (token && user) {
          set({ 
            token, 
            user: JSON.parse(user), 
            isAuthenticated: true 
          });
        }
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);