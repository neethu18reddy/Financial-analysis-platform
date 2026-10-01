export interface DatabaseHealth {
  status: string;
  dialect: string;
  connected: boolean;
  error?: string | null;
}

export interface HealthResponse {
  status: string;
  project_name: string;
  version: string;
  environment: string;
  timestamp: string;
  database: DatabaseHealth;
  system_info: {
    python_version?: string;
    os?: string;
    os_release?: string;
    debug?: boolean;
    [key: string]: any;
  };
}

export interface ApiError {
  message: string;
  code?: number;
  type?: string;
  details?: any;
}
