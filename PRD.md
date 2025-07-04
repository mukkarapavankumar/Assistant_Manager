# Product Requirements Document (PRD): Assistant Manager

## 1. Overview

**Assistant Manager** is a local Windows desktop application designed to automate repetitive team management workflows for managers. It connects to Outlook (via pywin32), uses a local LLM (via Ollama) for communication and summarization, and manages a Kanban board reflecting ongoing team activities. The assistant autonomously handles routine communication, task collection, follow-ups, Kanban updates, and reporting, requiring minimal manual intervention from the manager.

## 2. Goals & Objectives

- **Automate repetitive team update requests and follow-ups via email.**
- **Collect and organize team responses into a structured, up-to-date Kanban board.**
- **Track tasks and deadlines, sending reminders and follow-ups as needed.**
- **Maintain a local database of tasks, emails, and updates.**
- **Push manager-approved Kanban changes to a GitHub repo, updating a public GitHub Pages site.**
- **Enable the manager to query the assistant for status updates and summaries.**

## 3. User Roles

- **Manager:** Sets up and oversees the assistant, approves Kanban changes, queries for updates, and reviews summaries.
- **Team Member:** Receives and responds to emails generated by the assistant (no app access required).

## 4. Key Features & Requirements

### 4.1. Email Automation

- **Initial Setup:** Manager configures team member emails, update frequency, and preferred templates.
- **Automated Requests:** On a schedule (e.g., weekly), the assistant sends emails to all team members requesting updates on their current and planned work.
- **Customizable Templates:** Manager can edit the email template for requests and reminders.

### 4.2. Response Collection & Parsing

- **Inbox Monitoring:** Continuously monitor the Outlook inbox for replies from team members.
- **LLM-Powered Parsing:** Use the local LLM to extract structured task data (task name, description, due date, status) from free-form email responses.
- **Error Handling:** Notify the manager if a response cannot be parsed or is missing required info.

### 4.3. Kanban Board Management

- **Task Creation:** Automatically create or update Kanban board tasks based on parsed responses.
- **Status Tracking:** Move tasks across Kanban columns (To Do, In Progress, Done, Blocked, etc.) based on updates and deadlines.
- **Manual Adjustments:** Manager can manually edit, approve, or override Kanban board items before they are published.
- **Local Storage:** All data is stored locally, except when pushing Kanban updates to GitHub.

### 4.4. Follow-Ups and Reminders

- **Deadline Tracking:** Track task due dates and send automated reminder emails to team members as deadlines approach or are missed.
- **Escalation:** Notify the manager if a task is overdue or if a team member is unresponsive after repeated follow-ups.

### 4.5. Reporting & Summarization

- **Status Queries:** Manager can ask, “What’s going on with [team member/project/task]?” and the assistant generates a summary from the latest data.
- **Weekly Digest:** Optionally, generate and send a summary email to the manager (and/or team) with the current Kanban board status and highlights.

### 4.6. GitHub Integration

- **Kanban Publishing:** Upon manager approval, push the current Kanban board state to a GitHub repository.
- **GitHub Actions:** Trigger a workflow to update a public GitHub Pages site with the latest board.
- **Change History:** Maintain a log of Kanban changes and approvals.

### 4.7. User Interface

- **Dashboard:** Display the current Kanban board, task details, pending approvals, and recent communications.
- **Notifications:** Show alerts for unparsed responses, overdue tasks, and required manager actions.
- **Manual Controls:** Allow the manager to trigger email requests, approve Kanban changes, and query for summaries.

## 5. Non-Functional Requirements

- **Local-First:** All data and processing are local, except for Kanban board publishing to GitHub.
- **Security:** Store all sensitive data securely on the user’s machine.
- **Performance:** Must handle teams of up to 50 members with minimal lag.
- **Reliability:** Robust error handling for email parsing, Outlook connectivity, and Git operations.

## 6. Out of Scope

- Voice interface or chatbots
- Cloud-based storage (other than GitHub Kanban board)
- Direct team member access to the app

## 7. Example Workflow

1. **Setup:** Manager configures team, schedule, and email templates.
2. **Weekly Cycle:**
   - Assistant sends update request emails to all team members.
   - Collects and parses responses as they arrive.
   - Updates Kanban board accordingly.
   - Sends reminders/follow-ups as needed.
   - Notifies manager of issues (e.g., unresponsive members).
3. **Manager Review:**
   - Manager reviews and approves Kanban changes.
   - Approves publishing to GitHub.
4. **Reporting:**
   - Manager queries assistant for project/person/task status.
   - Assistant provides up-to-date summaries and highlights.

## 8. Success Criteria

- Manager spends significantly less time on routine update requests and follow-ups.
- Kanban board accurately reflects team activities with minimal manual input.
- All communications and data remain secure and local (except for the published board).
- The assistant reliably tracks, reminds, and summarizes as expected.
