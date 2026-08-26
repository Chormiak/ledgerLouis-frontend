// Categorias de Despensa/Receita personalizadas
export type CategoryType = 'income' | 'expense';

export interface Category {
  id?: string;
  name: string;
  type: CategoryType;
  description?: string;
  createdAt?: string;
}

// Participantes/Empregados
export interface CompanyParticipant {
  id?: string;
  name: string;
  email?: string;
  role: string;
  department?: string;
  salary?: number;
  joinDate?: string;
  createdAt?: string;
}

// Resposta do servidor para os endpoints
export interface CategoryResponse {
  success: boolean;
  message?: string;
  data?: Category | Category[];
}

export interface ParticipantResponse {
  success: boolean;
  message?: string;
  data?: CompanyParticipant | CompanyParticipant[];
}

