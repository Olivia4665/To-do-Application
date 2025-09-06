export interface User {
  username: string;
  email: string;
}

export interface Todo {
  id: number;
  title: string;
  description: string;
  completed: boolean;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, userData: User) => void;
  logout: () => void;
}