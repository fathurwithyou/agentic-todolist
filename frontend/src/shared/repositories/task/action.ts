import { tryCatch } from "../../lib/try-catch";
import type {
  GoogleTask,
  GoogleTaskList,
  CreateTaskRequest,
  UpdateTaskRequest,
  ParseTasksRequest
} from "../../types/task";

const BASE_URL = "/api/v1/tasks";

export const taskActions = {
  async getTaskLists(): Promise<GoogleTaskList[]> {
    const result = await tryCatch(async () => {
      const response = await fetch(`${BASE_URL}/lists`, {
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    });

    if (result.success) {
      return result.data;
    }

    throw new Error(result.error?.message || "Failed to fetch task lists");
  },

  async createTaskList(title: string): Promise<GoogleTaskList> {
    const result = await tryCatch(async () => {
      const response = await fetch(`${BASE_URL}/lists`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ title }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    });

    if (result.success) {
      return result.data;
    }

    throw new Error(result.error?.message || "Failed to create task list");
  },

  async getTasks(listId: string, includeCompleted = true): Promise<GoogleTask[]> {
    const result = await tryCatch(async () => {
      const response = await fetch(
        `${BASE_URL}/${listId}?include_completed=${includeCompleted}`,
        {
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    });

    if (result.success) {
      return result.data;
    }

    throw new Error(result.error?.message || "Failed to fetch tasks");
  },

  async createTask(listId: string, request: CreateTaskRequest): Promise<GoogleTask> {
    const result = await tryCatch(async () => {
      const response = await fetch(`${BASE_URL}/${listId}/tasks`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    });

    if (result.success) {
      return result.data;
    }

    throw new Error(result.error?.message || "Failed to create task");
  },

  async updateTask(listId: string, taskId: string, request: UpdateTaskRequest): Promise<GoogleTask> {
    const result = await tryCatch(async () => {
      const response = await fetch(`${BASE_URL}/${listId}/tasks/${taskId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    });

    if (result.success) {
      return result.data;
    }

    throw new Error(result.error?.message || "Failed to update task");
  },

  async deleteTask(listId: string, taskId: string): Promise<void> {
    const result = await tryCatch(async () => {
      const response = await fetch(`${BASE_URL}/${listId}/tasks/${taskId}`, {
        method: "DELETE",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    });

    if (!result.success) {
      throw new Error(result.error?.message || "Failed to delete task");
    }
  },

  async parseTimelineForTasks(listId: string, request: ParseTasksRequest) {
    const result = await tryCatch(async () => {
      const response = await fetch(`${BASE_URL}/${listId}/parse`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    });

    if (result.success) {
      return result.data;
    }

    throw new Error(result.error?.message || "Failed to parse timeline for tasks");
  },

  async syncTasks(listId: string): Promise<void> {
    const result = await tryCatch(async () => {
      const response = await fetch(`${BASE_URL}/${listId}/sync`, {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    });

    if (!result.success) {
      throw new Error(result.error?.message || "Failed to sync tasks");
    }
  },
};