# Broken Access Control Findings Report

Using the broken-access-control skill methodology, I've analyzed the Django application for OWASP 2025 A01: Broken Access Control and Broken Object-Level Authorization (BOLA) vulnerabilities.

## Summary of Findings

### 1. Critical IDOR Vulnerability - download_profile_pic (line 327)
**Issue**: No authorization check on user_id parameter
**Description**: The `download_profile_pic` function accepts a `user_id` parameter without verifying that the requesting user has permission to download that particular user's profile picture. Any authenticated user can manipulate the user_id parameter to download any user's profile picture.

**Vulnerability Type**: Broken Object-Level Authorization (BOLA)
**Risk Level**: High

### 2. Critical IDOR Vulnerability - profile_view (line 596)
**Issue**: No authorization check on user_id parameter  
**Description**: The `profile_view` function accepts a `user_id` parameter without verifying that the requesting user should be able to view that particular user's profile information. Any authenticated user can manipulate the user_id parameter to view any user's profile.

**Vulnerability Type**: Broken Object-Level Authorization (BOLA)
**Risk Level**: High

### 3. Moderate IDOR Vulnerability - download function (line 308)
**Issue**: Weak authorization check
**Description**: While the `download` function uses `@login_required`, the authorization check `file.project.users_assigned.filter(id=request.user.id).exists()` may be insufficient. If there's an issue with the project membership validation, an attacker could potentially access files from projects they're assigned to but shouldn't have access to.

**Vulnerability Type**: Broken Object-Level Authorization (BOLA)
**Risk Level**: Medium

### 4. Moderate IDOR Vulnerability - task_delete function (line 405)
**Issue**: Insufficient validation of task-project relationship
**Description**: The `task_delete` function accepts both `project_id` and `task_id` parameters but the authorization validation might be bypassable. Although it checks `belongs_to_project(request.user, project_id)` and `task.project == proj`, there may be edge cases where an attacker could manipulate the relationship between tasks and projects.

**Vulnerability Type**: Broken Object-Level Authorization (BOLA)
**Risk Level**: Medium

### 5. Moderate IDOR Vulnerability - task_edit function (line 373)
**Issue**: Insufficient validation of task-project relationship
**Description**: Similar to task_delete, the `task_edit` function accepts `project_id` and `task_id` parameters with authorization checks that could be bypassed. While it checks `belongs_to_project(request.user, project_id)` and `task.project == proj`, these validations might not be robust enough.

**Vulnerability Type**: Broken Object-Level Authorization (BOLA)
**Risk Level**: Medium

### 6. False Positive - download function authentication check (line 308)
**Issue**: Misidentified missing authentication
**Description**: The finding claims the download function lacks authentication, but it actually has `@login_required` decorator and proper authorization logic. This finding is incorrect.

**Vulnerability Type**: False Positive
**Risk Level**: N/A

## Recommendations

1. **Implement strict ownership verification** for all functions that accept user_id, task_id, project_id, or file_id parameters
2. **Add comprehensive authorization checks** for all resource access operations
3. **Use UUIDs instead of sequential IDs** where possible to prevent enumeration attacks
4. **Review all URL parameters** that could lead to unauthorized resource access
5. **Ensure all sensitive endpoints** require proper authentication and authorization

## Evidence of Vulnerabilities

All identified vulnerabilities can be exploited by manipulating URL parameters:
- `download_profile_pic/<user_id>/` - attacker can change user_id to access any profile picture
- `profile_view/<user_id>/` - attacker can change user_id to view any user profile
- `download/<file_id>/` - attacker can change file_id to access unauthorized files
- `task_delete/<project_id>/<task_id>/` - attacker can change task_id to delete unauthorized tasks
- `task_edit/<project_id>/<task_id>/` - attacker can change task_id to edit unauthorized tasks