const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export interface Ticket {
  id: number;
  title: string;
  description?: string;
  status: "new" | "in_progress" | "done";
  priority: "low" | "normal" | "high";
  created_at: string;
  updated_at: string;
}

export interface TicketListResponse {
  items: Ticket[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function handleResponse(response: Response) {
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new APIError(response.status, data.detail || "An error occurred");
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

export const api = {
  getCurrentUser: async (username: string, password: string): Promise<{ is_admin: boolean }> => {
    const auth = btoa(`${username}:${password}`);
    const response = await fetch(`${API_BASE}/api/users/me`, {
      headers: { Authorization: `Basic ${auth}` },
    });
    return handleResponse(response);
  },

  createTicket: async (ticket: { title: string; description?: string; priority: string }) => {
    const response = await fetch(`${API_BASE}/api/tickets`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(ticket),
    });
    return handleResponse(response);
  },

  getTickets: async (params: {
    search?: string;
    status?: string;
    priority?: string;
    sort_by?: string;
    sort_order?: string;
    page?: number;
    page_size?: number;
  }): Promise<TicketListResponse> => {
    const endpoint = `${API_BASE}/api/tickets`;
    const queryParams = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        queryParams.append(key, String(value));
      }
    });

    const queryString = queryParams.toString();
    const fullUrl = queryString ? `${endpoint}?${queryString}` : endpoint;

    const response = await fetch(fullUrl);
    return handleResponse(response);
  },

  getTicket: async (id: number): Promise<Ticket> => {
    const response = await fetch(`${API_BASE}/api/tickets/${id}`);
    return handleResponse(response);
  },

  updateTicketStatus: async (id: number, status: string): Promise<Ticket> => {
    const response = await fetch(`${API_BASE}/api/tickets/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });
    return handleResponse(response);
  },

  deleteTicket: async (id: number, username: string, password: string): Promise<void> => {
    const auth = btoa(`${username}:${password}`);
    const response = await fetch(`${API_BASE}/api/tickets/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Basic ${auth}` },
    });
    return handleResponse(response);
  },
};
