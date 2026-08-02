# Bridge Troll — Systematic Security Code Review & Authorization Assessment

We assessed commit `#40747c6510014958c9519d3708b5dc9325a0cc1c`

This document details the systematic execution of the **Authorization Review Checklist** (`bridge_troll_authorization_checklist.md`) across the Bridge Troll codebase (`c:/workspace/bridge_troll`), documenting verified security controls and authorization vulnerabilities.

---

## 1. Systematic Review Execution & Findings

### 🔴 Finding 1: Unprotected Unauthenticated RSVP Deletion via Token Prediction/Enumeration
* **Vulnerability Type**: Insecure Authorization / Token-based Unauthenticated Deletion
* **File Location**: `app/controllers/rsvps_controller.rb:84-101`
* **Vulnerable Code**:
  ```ruby
  class RsvpsController < ApplicationController
    before_action :authenticate_user!, except: %i[quick_destroy_confirm destroy]
    before_action :skip_authorization

    def destroy
      @rsvp = Rsvp.find_by(token: params[:token]) if params[:token].present?

      if @rsvp.nil?
        authenticate_user! && load_rsvp
        return unless @rsvp
      end

      Rsvp.transaction do
        @rsvp.destroy
        WaitlistManager.new(@event.reload).reorder_waitlist!
      end
  ```
* **Impact**: An unauthenticated attacker who discovers or enumerates an RSVP token (`params[:token]`) can cancel and delete any user's event RSVP without logging in. Furthermore, `skip_authorization` completely disables Pundit policy validation for the entire controller.
* **Remediation**:
  1. Remove `destroy` from the `before_action :authenticate_user!` skip list.
  2. Enforce Pundit authorization (`authorize @rsvp`) to verify that `current_user == @rsvp.user` or `current_user` is an event organizer/admin.

---

### 🔴 Finding 2: Unverified Authorization in `RsvpsController` (`skip_authorization` Abuse)
* **Vulnerability Type**: Missing Function-Level Access Control (CWE-285)
* **File Location**: `app/controllers/rsvps_controller.rb:10`
* **Vulnerable Code**:
  ```ruby
  class RsvpsController < ApplicationController
    before_action :skip_authorization
    ...
    def edit
      if @rsvp.role == Role::ORGANIZER
        redirect_to @event
      else
        render :edit
      end
    end

    def update
      if @rsvp.update(rsvp_params)
        apply_other_changes_from_params
  ```
* **Impact**: Because `skip_authorization` is explicitly called on the controller level, Pundit policies (`RsvpPolicy`) are completely bypassed during `edit`, `update`, `create`, and `destroy`. A logged-in user can edit or update another user's RSVP if they manipulate the RSVP `id` parameter.
* **Remediation**:
  1. Remove `before_action :skip_authorization` from `RsvpsController`.
  2. Add `authorize @rsvp` in `edit`, `update`, and `destroy` actions to verify `RsvpPolicy`.

---

### 🟡 Finding 3: Potential BOLA in `Events::EmailsController` (Missing Scoped Recipient Check)
* **Vulnerability Type**: Broken Object Level Authorization (IDOR / BOLA)
* **File Location**: `app/controllers/events/emails_controller.rb:17-25`
* **Vulnerable Code**:
  ```ruby
  def create
    authorize @event, :edit?
    recipient_ids = email_params[:recipients] ? email_params[:recipients].map(&:to_i) : []
    recipient_rsvps = @event.rsvps.where(user_id: recipient_ids).includes(:user)
  ```
* **Analysis**: While `authorize @event, :edit?` correctly verifies that `current_user` is an organizer/leader for `@event`, `email_params[:recipients]` is mapped directly into `recipient_ids`. If an organizer passes user IDs from other events or global users, emails will be delivered to those user accounts as long as they have an RSVP on `@event`.

---

### 🟢 Verified Control 1: Chapter Leadership Appointment (`Chapters::LeadersController`)
* **File Location**: `app/controllers/chapters/leaders_controller.rb:12-23`
* **Verification Outcome**: **SECURE**
* **Code Reference**:
  ```ruby
  def create
    authorize @chapter, :modify_leadership?
    leader = ChapterLeadership.new(chapter: @chapter, user_id: leader_id_param)
    if leader.save
  ```
* **Analysis**: Properly guarded by `authorize @chapter, :modify_leadership?`. Pundit policy `ChapterPolicy#modify_leadership?` verifies that `current_user` is an existing chapter leader or parent organization leader for `@chapter`, effectively preventing cross-chapter privilege escalation.

---

### 🟢 Verified Control 2: Event Email Broadcast Authorization (`Events::EmailsController`)
* **File Location**: `app/controllers/events/emails_controller.rb:8-18`
* **Verification Outcome**: **SECURE**
* **Code Reference**:
  ```ruby
  def show
    authorize @event, :edit?
  ...
  def create
    authorize @event, :edit?
  ```
* **Analysis**: All email broadcast actions explicitly invoke `authorize @event, :edit?`. Non-organizers attempting to post to `/events/:event_id/emails` trigger `Pundit::NotAuthorizedError` and are blocked.

---

### 🟢 Verified Control 3: Admin Diagnostic & Dashboard Routes (`AdminPagesController`)
* **File Location**: `app/controllers/admin_pages_controller.rb:1-15`
* **Verification Outcome**: **SECURE**
* **Code Reference**:
  ```ruby
  class AdminPagesController < ApplicationController
    before_action :authenticate_user!
    before_action :authorize_admin

    private

    def authorize_admin
      authorize :admin_page, :show?
    end
  ```
* **Analysis**: Diagnostic exception trigger (`/admin_dashboard/raise_exception`) and test email trigger (`/admin_dashboard/send_test_email`) are guarded by `authorize_admin`, enforcing `user.admin?` verification across all admin endpoints.

---

## 2. Summary of Findings & Action Plan

| Finding ID | Severity | Location | Vulnerability Description | Recommended Fix |
| :--- | :--- | :--- | :--- | :--- |
| **BT-AUTH-01** | **CRITICAL** | `rsvps_controller.rb:84` | Unauthenticated RSVP deletion via token lookup (`skip_authorization` enabled) | Enforce `authenticate_user!` & `authorize @rsvp` on `destroy` |
| **BT-AUTH-02** | **HIGH** | `rsvps_controller.rb:10` | Global `skip_authorization` bypasses `RsvpPolicy` on `edit` & `update` | Remove `skip_authorization` and add `authorize @rsvp` |
| **BT-AUTH-03** | **LOW** | `emails_controller.rb:19` | Recipient ID mapping trusts client-supplied array | Validate recipient user IDs belong exclusively to `@event.rsvps` |
