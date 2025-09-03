export type TaskStatus = "needsAction" | "completed";

export type TaskPriority = "high" | "medium" | "low";

export interface GoogleTask {
  task_id: string;
  title: string;
  notes?: string;
  status: TaskStatus;
  due?: string;
  completed?: string;
  priority?: TaskPriority;
  parent?: string;
  web_view_link?: string;
  created_at?: string;
  updated_at?: string;
}

export interface GoogleTaskList {
  list_id: string;
  title: string;
  task_count?: number;
  created_at?: string;
  updated_at?: string;
}

export interface CreateTaskRequest {
  title: string;
  notes?: string;
  due_date?: string;
  due_time?: string;
  priority?: TaskPriority;
  parent_task?: string;
  list_id?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  notes?: string;
  due_date?: string;
  due_time?: string;
  priority?: TaskPriority;
  completed?: boolean;
}

export interface ParseTasksRequest {
  timeline_text: string;
  list_id?: string;
  provider?: string;
  model?: string;
}