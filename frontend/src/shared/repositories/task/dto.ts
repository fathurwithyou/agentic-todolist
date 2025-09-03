import type { GoogleTask, GoogleTaskList, CreateTaskRequest, UpdateTaskRequest, ParseTasksRequest } from "../../types/task";

export interface TaskListsResponse {
  success: boolean;
  data: GoogleTaskList[];
}

export interface TasksResponse {
  success: boolean;
  data: GoogleTask[];
}

export interface CreateTaskResponse {
  success: boolean;
  data: GoogleTask;
}

export interface ParseTasksResponse {
  success: boolean;
  created_count: number;
  total_count: number;
  tasks: GoogleTask[];
  provider_used: string;
  model_used: string;
  processing_time_ms: number;
}