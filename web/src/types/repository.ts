export interface Repository {
  id: string;
  name: string;
  url: string;
}

export interface ValidationError {
  field: string;
  message: string;
}

export interface ApiError {
  message: string;
  errors?: ValidationError[];
  status?: number;
}
