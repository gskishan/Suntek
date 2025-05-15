frappe.ui.form.on("Project", {
    refresh: function (frm) {
        if (frm.doc.custom_type_of_case != "Subsidy" || frm.doc.custom_type_of_case != "Non Subsidy") {
            $('.document-link[data-doctype="Discom"] .btn[data-doctype="Discom"]').remove();
        }
        if (!frm.doc.custom_type_of_case == "Subsidy") {
            $('.document-link[data-doctype="Subsidy"] .btn[data-doctype="Subsidy"]').remove();
        }

        if (!frm.is_new() && frm.doc.custom_project_template) {
            frm.set_df_property("custom_project_template", "read_only", 1);
        }
        frm.clear_custom_buttons();

        if (!frm.is_new()) {
            show_task_timeline(frm);
        }

        if (frm.doc.custom_type_of_case == "Subsidy") {
            if (!frm.doc.custom_discom_id) {
                frm.add_custom_button(
                    __("Discom"),
                    function () {
                        frappe.model.with_doctype("Discom", function () {
                            var discomDoc = frappe.model.get_new_doc("Discom");
                            discomDoc.project_name = frm.doc.name;
                            discomDoc.sales_order = frm.doc.sales_order;
                            discomDoc.customer_name = frm.doc.customer;

                            frappe.set_route("Form", "Discom", discomDoc.name);
                        });
                    },
                    __("Create"),
                );
            }
            if (!frm.doc.custom_subsidy_id) {
                frm.add_custom_button(
                    __("Subsidy"),
                    function () {
                        frappe.model.with_doctype("Subsidy", function () {
                            var subsidyDoc = frappe.model.get_new_doc("Subsidy");
                            subsidyDoc.project_name = frm.doc.name;
                            subsidyDoc.sales_order = frm.doc.sales_order;
                            subsidyDoc.customer_name = frm.doc.customer;
                            frappe.set_route("Form", "Subsidy", subsidyDoc.name);
                        });
                    },
                    __("Create"),
                );
            }
        } else if (frm.doc.custom_type_of_case == "Non Subsidy") {
            if (!frm.doc.custom_discom_id) {
                frm.add_custom_button(
                    __("Discom"),
                    function () {
                        frappe.model.with_doctype("Discom", function () {
                            var discomDoc = frappe.model.get_new_doc("Discom");
                            discomDoc.project_name = frm.doc.name;
                            discomDoc.sales_order = frm.doc.sales_order;
                            discomDoc.customer_name = frm.doc.customer;
                            frappe.set_route("Form", "Discom", discomDoc.name);
                        });
                    },
                    __("Create"),
                );
            }
        }
    },
});

function show_task_timeline(frm) {
    frm.set_df_property("custom_task_timeline", "options", '<div class="text-muted">Loading Task Timeline</div>');

    // First fetch tasks
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Task",
            filters: {
                project: frm.doc.name,
            },
            fields: ["name", "subject", "status", "exp_start_date", "exp_end_date", "progress"],
            order_by: "exp_start_date asc",
        },
        callback: function (r) {
            if (r.message && r.message.length > 0) {
                // Fetch assigned users for each task
                const tasks = r.message;
                const taskNames = tasks.map((task) => task.name);

                try {
                    frappe.call({
                        method: "frappe.client.get_list",
                        args: {
                            doctype: "ToDo",
                            filters: {
                                reference_type: "Task",
                                reference_name: ["in", taskNames],
                            },
                            fields: ["reference_name", "allocated_to", "owner"],
                        },
                        callback: function (todoResponse) {
                            try {
                                const taskAssignments = {};

                                // Group todos by task
                                if (todoResponse.message && Array.isArray(todoResponse.message)) {
                                    todoResponse.message.forEach((todo) => {
                                        if (todo && todo.reference_name) {
                                            if (!taskAssignments[todo.reference_name]) {
                                                taskAssignments[todo.reference_name] = [];
                                            }
                                            const assignedUser = todo.allocated_to || todo.owner;
                                            if (
                                                assignedUser &&
                                                !taskAssignments[todo.reference_name].includes(assignedUser)
                                            ) {
                                                taskAssignments[todo.reference_name].push(assignedUser);
                                            }
                                        }
                                    });
                                }

                                render_task_timeline(frm, tasks, taskAssignments);
                            } catch (todoError) {
                                console.error("Error processing ToDo data:", todoError);
                                // Fall back to rendering without assignments
                                render_task_timeline(frm, tasks, {});
                            }
                        },
                        error: function (err) {
                            console.error("Error fetching ToDos:", err);
                            // Fall back to rendering without assignments
                            render_task_timeline(frm, tasks, {});
                        },
                    });
                } catch (fetchError) {
                    console.error("Error in ToDo fetch setup:", fetchError);
                    // Fall back to rendering without assignments
                    render_task_timeline(frm, tasks, {});
                }
            } else {
                frm.set_df_property(
                    "custom_task_timeline",
                    "options",
                    '<div class="text-muted">No tasks found for this project</div>',
                );
            }
        },
    });
}

// Global function for managing task assignees
window.manage_task_assignees = function (task_name) {
    if (!task_name) return;

    // Decode HTML entities if needed (like &#39; -> ')
    task_name = $("<div/>").html(task_name).text();

    // Create a dialog to manage assignees
    const d = new frappe.ui.Dialog({
        title: __("Manage Task Assignees"),
        fields: [
            {
                label: __("Task"),
                fieldname: "task",
                fieldtype: "Link",
                options: "Task",
                default: task_name,
                read_only: 1,
            },
            {
                fieldtype: "Section Break",
                label: __("Assign Individual User"),
            },
            {
                label: __("Assign To User"),
                fieldname: "assign_to",
                fieldtype: "Link",
                options: "User",
                description: __("Select a user to assign to this task"),
            },
            {
                fieldname: "assign_btn",
                fieldtype: "Button",
                label: __("Add User"),
                click: function () {
                    const user = d.get_value("assign_to");
                    if (!user) {
                        frappe.throw(__("Please select a user to assign"));
                        return;
                    }

                    assign_single_user(user);
                },
            },
            {
                fieldtype: "Section Break",
                label: __("Assign User Group"),
            },
            {
                label: __("User Group"),
                fieldname: "user_group",
                fieldtype: "Link",
                options: "User Group",
                description: __("Select a User Group to assign all members to this task"),
            },
            {
                fieldname: "group_assign_btn",
                fieldtype: "Button",
                label: __("Add Group Members"),
                click: function () {
                    const group = d.get_value("user_group");
                    if (!group) {
                        frappe.throw(__("Please select a User Group"));
                        return;
                    }

                    assign_user_group(group);
                },
            },
            {
                fieldtype: "Section Break",
                label: __("Current Assignees"),
            },
            {
                fieldname: "assignee_list",
                fieldtype: "HTML",
            },
            {
                fieldtype: "Section Break",
                label: __("Group Assignments"),
            },
            {
                fieldname: "group_assignment_list",
                fieldtype: "HTML",
                description: __("Users assigned via groups"),
            },
        ],
        primary_action_label: __("Done"),
        primary_action: function () {
            d.hide();
            // Refresh the project form to update the timeline
            cur_frm.reload_doc();
        },
    });

    d.show();

    // Currently assigned users and groups
    let current_assignments = [];
    let group_assignments = {};

    // Function to assign a single user
    function assign_single_user(user) {
        frappe.call({
            method: "frappe.desk.form.assign_to.add",
            args: {
                doctype: "Task",
                name: task_name,
                assign_to: [user],
            },
            callback: function (r) {
                if (r.message) {
                    frappe.show_alert({
                        message: __("Task {0} assigned to {1}", [task_name, user]),
                        indicator: "green",
                    });

                    // Clear the input
                    d.set_value("assign_to", "");

                    // Refresh the current assignees
                    refresh_assignee_list();
                } else if (r.exc) {
                    console.error("Error adding assignment:", r);
                    frappe.show_alert({
                        message: __("Error assigning task: {0}", [r.exc || "Unknown error"]),
                        indicator: "red",
                    });
                }
            },
        });
    }

    // Function to assign all users in a group
    function assign_user_group(group_name) {
        // Instead of directly querying User Group Member, use the assign_to method with the group
        frappe.show_alert({
            message: __("Assigning group {0} to task...", [group_name]),
            indicator: "blue",
        });

        // First try to locate the task to confirm it exists
        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Task",
                name: task_name,
            },
            callback: function (r) {
                if (r.message) {
                    // The task exists, now use a simple method to handle group assignment
                    // We'll use a custom approach here - first get if the group exists
                    frappe.call({
                        method: "frappe.client.get",
                        args: {
                            doctype: "User Group",
                            name: group_name,
                        },
                        callback: function (group_response) {
                            if (group_response.message) {
                                // Group exists, store it in our tracking
                                if (!group_assignments[group_name]) {
                                    group_assignments[group_name] = [__("Group Members")];
                                }

                                // Update the UI
                                refresh_group_assignments();

                                // Make a direct call to assign this group to the task
                                // Instead of getting all users, we'll use a group marker
                                frappe.call({
                                    method: "frappe.desk.form.assign_to.add",
                                    args: {
                                        doctype: "Task",
                                        name: task_name,
                                        assign_to: [group_name + " (Group)"],
                                        description: __("Group Assignment: All users in {0}", [group_name]),
                                    },
                                    callback: function (assign_response) {
                                        if (assign_response.message) {
                                            frappe.show_alert({
                                                message: __("Group {0} assigned to task", [group_name]),
                                                indicator: "green",
                                            });

                                            // Clear the input and refresh
                                            d.set_value("user_group", "");
                                            refresh_assignee_list();
                                        } else {
                                            frappe.show_alert({
                                                message: __("Failed to assign group {0}", [group_name]),
                                                indicator: "red",
                                            });
                                        }
                                    },
                                });
                            } else {
                                frappe.show_alert({
                                    message: __("User Group {0} not found", [group_name]),
                                    indicator: "red",
                                });
                            }
                        },
                    });
                } else {
                    frappe.show_alert({
                        message: __("Task {0} not found", [task_name]),
                        indicator: "red",
                    });
                }
            },
        });
    }

    // Function to refresh the assignee list
    function refresh_assignee_list() {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "ToDo",
                filters: {
                    reference_type: "Task",
                    reference_name: task_name,
                    status: "Open",
                },
                fields: ["name", "allocated_to", "owner"],
            },
            callback: function (r) {
                console.log("ToDos for task:", r.message);
                if (r.message) {
                    // Store current assignments for reference
                    current_assignments = r.message;

                    let assignee_html = '<div class="assignee-list">';

                    if (r.message.length === 0) {
                        assignee_html += '<div class="text-muted">No assignees</div>';
                    } else {
                        r.message.forEach((todo) => {
                            const assignee = todo.allocated_to || todo.owner;

                            // Check if we have the todo name
                            if (!todo.name) {
                                console.warn("Missing ToDo name for:", todo);
                                return;
                            }

                            assignee_html += `
                                <div class="assignee-item" style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border-color);">
                                    <div>${frappe.utils.escape_html(assignee)}</div>
                                    <button class="btn btn-xs btn-danger" 
                                        onclick="direct_remove_assign('${task_name}', '${todo.name}', this)">
                                        ${__("Remove")}
                                    </button>
                                </div>
                            `;
                        });
                    }

                    assignee_html += "</div>";
                    d.fields_dict.assignee_list.$wrapper.html(assignee_html);

                    // Also refresh group assignments
                    refresh_group_assignments();
                }
            },
            error: function (err) {
                console.error("Error fetching assignments:", err);
                d.fields_dict.assignee_list.$wrapper.html(
                    '<div class="alert alert-danger">Error loading assignees. Please try again.</div>',
                );
            },
        });
    }

    // Function to refresh group assignments
    function refresh_group_assignments() {
        // Simplified approach - just show the groups we've tracked
        let groups_html = '<div class="group-assignments">';

        if (Object.keys(group_assignments).length === 0) {
            groups_html += '<div class="text-muted">No group assignments</div>';
        } else {
            // For each group we've assigned, show a card
            Object.keys(group_assignments).forEach((group) => {
                groups_html += `
                    <div class="group-item" style="margin-bottom: 15px; padding: 10px; background-color: var(--control-bg); border-radius: 4px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <strong>${frappe.utils.escape_html(group)}</strong>
                            <button class="btn btn-xs btn-danger" 
                                onclick="remove_group_assignment('${task_name}', '${group}', this)">
                                ${__("Unassign Group")}
                            </button>
                        </div>
                        <div class="text-muted">${__("All members of this group will be notified")}</div>
                    </div>
                `;
            });
        }

        groups_html += "</div>";
        d.fields_dict.group_assignment_list.$wrapper.html(groups_html);
    }

    // Initial load of assignees
    refresh_assignee_list();
};

// Function to remove a group assignment
window.remove_group_assignment = function (taskName, groupName, buttonElement) {
    if (!taskName || !groupName) {
        console.error("Missing required parameters for group unassignment");
        return;
    }

    // Disable the button to prevent multiple clicks
    $(buttonElement).prop("disabled", true).html('<i class="fa fa-spinner fa-spin"></i>');

    // Find the todo entry for the group assignment
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "ToDo",
            filters: {
                reference_type: "Task",
                reference_name: taskName,
                allocated_to: ["like", "%" + groupName + "%"],
                status: "Open",
            },
            fields: ["name"],
        },
        callback: function (r) {
            if (r.message && r.message.length > 0) {
                // Found matching todos, delete them
                let deleted = 0;
                let errors = 0;

                r.message.forEach((todo) => {
                    frappe.call({
                        method: "frappe.client.delete",
                        args: {
                            doctype: "ToDo",
                            name: todo.name,
                        },
                        callback: function (delRes) {
                            if (!delRes.exc) {
                                deleted++;
                            } else {
                                errors++;
                            }

                            // If all processed
                            if (deleted + errors === r.message.length) {
                                if (deleted > 0) {
                                    // Remove from our tracking
                                    if (group_assignments[groupName]) {
                                        delete group_assignments[groupName];
                                    }

                                    // Remove from UI
                                    $(buttonElement)
                                        .closest(".group-item")
                                        .slideUp(300, function () {
                                            $(this).remove();

                                            // If no more groups
                                            if (Object.keys(group_assignments).length === 0) {
                                                $(".group-assignments").html(
                                                    '<div class="text-muted">No group assignments</div>',
                                                );
                                            }
                                        });

                                    frappe.show_alert({
                                        message: __("Unassigned group {0}", [groupName]),
                                        indicator: errors > 0 ? "yellow" : "green",
                                    });

                                    // Refresh the form after a delay
                                    setTimeout(function () {
                                        if (cur_frm) cur_frm.reload_doc();
                                    }, 1000);
                                } else {
                                    $(buttonElement).prop("disabled", false).text(__("Unassign Group"));
                                    frappe.show_alert({
                                        message: __("Failed to remove group assignment"),
                                        indicator: "red",
                                    });
                                }
                            }
                        },
                    });
                });
            } else {
                // No todos found
                $(buttonElement).prop("disabled", false).text(__("Unassign Group"));
                frappe.show_alert({
                    message: __("No assignments found for group {0}", [groupName]),
                    indicator: "orange",
                });
            }
        },
        error: function () {
            $(buttonElement).prop("disabled", false).text(__("Unassign Group"));
            frappe.show_alert({
                message: __("Error checking group assignments"),
                indicator: "red",
            });
        },
    });
};

// Function to remove an assignee
window.remove_task_assignee = function (todo_name, task_name) {
    if (!todo_name || !task_name) {
        console.error("Missing required parameters:", { todo_name, task_name });
        return;
    }

    // Decode HTML entities if needed
    task_name = $("<div/>").html(task_name).text();

    // Use the correct API format for todo removal
    frappe.call({
        method: "frappe.desk.form.assign_to.remove",
        args: {
            doctype: "Task",
            name: task_name,
            assign_to: todo_name,
        },
        callback: function (r) {
            if (!r.exc) {
                frappe.show_alert({
                    message: __("Assignment removed"),
                    indicator: "green",
                });

                // Try a different approach - refresh the current form
                if (cur_frm) {
                    cur_frm.reload_doc();
                }

                // Close any open dialog (in case the dialog is still open)
                $(".modal.show").modal("hide");

                // Re-show the assignments dialog after a short delay to allow the server to update
                setTimeout(function () {
                    manage_task_assignees(task_name);
                }, 500);
            } else {
                console.error("Error removing assignment:", r);
                frappe.show_alert({
                    message: __("Error removing assignment: {0}", [r.exc || "Unknown error"]),
                    indicator: "red",
                });
            }
        },
    });
};

// Safely handle task assignment clicks
window.handleTaskAssignment = function (element) {
    const taskId = element && element.dataset ? element.dataset.task : null;
    if (taskId) {
        manage_task_assignees(taskId);
    }
};

function render_task_timeline(frm, tasks, taskAssignments) {
    try {
        let html = '<div class="task-timeline">';
        html += `<style>
            .task-timeline { padding: 15px; }
            .timeline-item { display: flex; margin-bottom: 10px; align-items: center; }
            .timeline-dot { 
                width: 20px; height: 20px; border-radius: 50%; margin-right: 15px; flex-shrink: 0; 
                border: 2px solid var(--border-color);
            }
            .timeline-line { 
                height: 30px; width: 2px; background-color: var(--border-color); margin-left: 9px; 
            }
            .task-complete { background-color: var(--primary); }
            .task-ongoing { background-color: var(--warning); }
            .task-pending { background-color: var(--gray-500); }
            .task-content { 
                flex-grow: 1; 
                border-left: 3px solid var(--border-color); 
                padding: 10px 15px; 
                background-color: var(--card-bg);
                border-radius: 4px;
                box-shadow: var(--shadow-sm);
                display: flex;
                justify-content: space-between;
            }
            .task-content-text {
                flex-grow: 1;
            }
            .task-progress { height: 5px; background-color: var(--gray-300); margin-top: 5px; border-radius: 3px; }
            .task-progress-bar { height: 100%; background-color: var(--primary); border-radius: 3px; }
            .task-assignments {
                display: flex;
                flex-shrink: 0;
                margin-left: 10px;
                align-items: center;
                cursor: pointer;
                padding: 5px;
                border-radius: 16px;
                transition: background-color 0.2s;
            }
            .task-assignments:hover {
                background-color: var(--control-bg);
            }
            .task-avatar {
                width: 28px;
                height: 28px;
                border-radius: 50%;
                background-size: cover;
                background-position: center;
                margin-left: -8px;
                border: 2px solid var(--card-bg);
                position: relative;
                overflow: hidden;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: var(--gray-300);
                color: var(--text-color);
                font-weight: 500;
                font-size: 11px;
            }
            .task-avatar:first-child {
                margin-left: 0;
            }
            .avatar-count {
                background-color: var(--gray-600);
                color: var(--white);
                width: 28px;
                height: 28px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 10px;
                border: 2px solid var(--card-bg);
            }
            .task-assign-btn {
                width: 28px;
                height: 28px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: var(--control-bg);
                color: var(--text-color);
                border: 1px dashed var(--gray-500);
                cursor: pointer;
                font-size: 14px;
                margin-left: 5px;
            }
            .task-assign-btn:hover {
                background-color: var(--control-bg-on-hover);
            }
        </style>`;

        tasks.forEach((task, index) => {
            let statusClass = "task-pending";
            if (task.status === "Completed") {
                statusClass = "task-complete";
            } else if (task.status === "Working" || task.status === "Open" || task.status === "In Progress") {
                statusClass = "task-ongoing";
            }

            // Generate assignment avatars HTML
            let assignmentsHtml = "";
            const taskUsers =
                taskAssignments && task && task.name && taskAssignments[task.name] ? taskAssignments[task.name] : [];
            const maxAvatars = 3;

            // Use a safer approach to avoid quote issues
            const safeTaskName = task.name.replace(/['"\\]/g, function (c) {
                return "&#" + c.charCodeAt(0) + ";";
            });

            // Create a clickable area that opens assignment dialog with data attribute
            assignmentsHtml = `<div class="task-assignments" data-task="${safeTaskName}" onclick="handleTaskAssignment(this)">`;

            if (Array.isArray(taskUsers) && taskUsers.length > 0) {
                taskUsers.slice(0, maxAvatars).forEach((user) => {
                    if (user) {
                        try {
                            // Get user's first name initial or use the first character of their email
                            const userInitial = (user.charAt(0) || "").toUpperCase();

                            // Create an avatar with the user's initial
                            assignmentsHtml += `
                                <div class="task-avatar" title="${frappe.utils.escape_html(user) || "Unknown user"}">
                                    ${userInitial}
                                </div>`;
                        } catch (userError) {
                            console.warn("Error processing user:", user, userError);
                            assignmentsHtml += `<div class="task-avatar" title="${
                                frappe.utils.escape_html(user) || "Unknown user"
                            }">?</div>`;
                        }
                    }
                });

                // Add +X more indicator if there are additional users
                if (taskUsers.length > maxAvatars) {
                    assignmentsHtml += `<div class="avatar-count" title="${
                        taskUsers.length - maxAvatars
                    } more users">+${taskUsers.length - maxAvatars}</div>`;
                }
            }

            // Add "plus" button to indicate you can add assignees
            assignmentsHtml += `<div class="task-assign-btn" title="Manage assignees">+</div>`;
            assignmentsHtml += "</div>";

            html += `<div class="timeline-item">
                <div class="timeline-dot ${statusClass}"></div>
                <div class="task-content">
                    <div class="task-content-text">
                        <div><strong>${
                            task.subject || "Untitled Task"
                        }</strong> <a href="/app/task/${encodeURIComponent(task.name)}">${task.name}</a></div>
                        <div class="text-muted">Status: ${task.status || "Not Set"} | ${
                task.exp_start_date || "No start date"
            } → ${task.exp_end_date || "No end date"}</div>
                        <div class="task-progress">
                            <div class="task-progress-bar" style="width: ${task.progress || 0}%"></div>
                        </div>
                    </div>
                    ${assignmentsHtml}
                </div>
            </div>`;

            if (index < tasks.length - 1) {
                html += '<div class="timeline-line"></div>';
            }
        });

        html += "</div>";
        frm.set_df_property("custom_task_timeline", "options", html);
    } catch (renderError) {
        console.error("Error rendering task timeline:", renderError);
        frm.set_df_property(
            "custom_task_timeline",
            "options",
            '<div class="alert alert-warning">Error rendering task timeline. Please refresh the page and try again.</div>',
        );
    }
}

// Direct remove assignment function
window.direct_remove_assign = function (taskName, todoName, buttonElement) {
    if (!taskName || !todoName) {
        console.error("Missing required parameters to remove assignment");
        return;
    }

    // Disable the button to prevent multiple clicks
    $(buttonElement).prop("disabled", true).html('<i class="fa fa-spinner fa-spin"></i>');

    // Try a more direct approach - delete the ToDo document
    frappe.call({
        method: "frappe.client.delete",
        args: {
            doctype: "ToDo",
            name: todoName,
        },
        callback: function (response) {
            $(buttonElement).prop("disabled", false).html(__("Remove"));

            if (!response.exc) {
                // Show success message
                frappe.show_alert({
                    message: __("Assignment removed"),
                    indicator: "green",
                });

                // Remove the row from the UI immediately for better UX
                $(buttonElement)
                    .closest(".assignee-item")
                    .slideUp(300, function () {
                        $(this).remove();

                        // Check if no more assignees
                        if ($(".assignee-item").length === 0) {
                            $(".assignee-list").html('<div class="text-muted">No assignees</div>');
                        }
                    });

                // Refresh the form, but after a delay
                setTimeout(function () {
                    if (cur_frm) cur_frm.reload_doc();
                }, 1000);
            } else {
                console.error("Error removing assignment:", response);
                frappe.show_alert({
                    message:
                        __("Failed to remove assignment: ") + (response.exc_message || response.exc || "Unknown error"),
                    indicator: "red",
                });

                // If we get permission error, try the second approach
                if (response.exc && response.exc.includes("Permission")) {
                    try_alternative_removal(taskName, todoName, buttonElement);
                }
            }
        },
    });
};

// Alternative approach if direct deletion fails
function try_alternative_removal(taskName, todoName, buttonElement) {
    frappe.call({
        method: "frappe.desk.form.assign_to.remove",
        args: {
            doctype: "Task",
            name: taskName,
            assign_to: todoName,
        },
        callback: function (response) {
            if (!response.exc) {
                // Show success message
                frappe.show_alert({
                    message: __("Assignment removed (alternative method)"),
                    indicator: "green",
                });

                // Remove the row from the UI
                $(buttonElement)
                    .closest(".assignee-item")
                    .slideUp(300, function () {
                        $(this).remove();
                    });

                // Refresh the form
                setTimeout(function () {
                    if (cur_frm) cur_frm.reload_doc();
                }, 1000);
            } else {
                // Try one last method as a fallback
                frappe.call({
                    method: "frappe.desk.doctype.todo.todo.remove_assignment",
                    args: {
                        doctype: "Task",
                        name: taskName,
                        assigned_by: frappe.session.user,
                    },
                    callback: function (final_response) {
                        if (!final_response.exc) {
                            frappe.show_alert({
                                message: __("Assignment removed (fallback method)"),
                                indicator: "green",
                            });

                            setTimeout(function () {
                                if (cur_frm) cur_frm.reload_doc();
                            }, 1000);
                        } else {
                            frappe.show_alert({
                                message: __("All removal methods failed. Please try reloading the page."),
                                indicator: "red",
                            });
                        }
                    },
                });
            }
        },
    });
}
