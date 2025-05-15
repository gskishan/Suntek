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

                                render_task_timeline(frm, tasks, {});
                            }
                        },
                        error: function (err) {
                            console.error("Error fetching ToDos:", err);

                            render_task_timeline(frm, tasks, {});
                        },
                    });
                } catch (fetchError) {
                    console.error("Error in ToDo fetch setup:", fetchError);

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

window.manage_task_assignees = function (task_name) {
    if (!task_name) return;

    task_name = $("<div/>").html(task_name).text();

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
                label: __("Current Assignees"),
            },
            {
                fieldname: "assignee_list",
                fieldtype: "HTML",
            },
        ],
        primary_action_label: __("Done"),
        primary_action: function () {
            d.hide();
            cur_frm.reload_doc();
        },
    });

    d.show();

    let current_assignments = [];

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

                    d.set_value("assign_to", "");
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
                    current_assignments = r.message;

                    let assignee_html = '<div class="assignee-list">';

                    if (r.message.length === 0) {
                        assignee_html += '<div class="text-muted">No assignees</div>';
                    } else {
                        r.message.forEach((todo) => {
                            const assignee = todo.allocated_to || todo.owner;

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

    refresh_assignee_list();
};

window.remove_task_assignee = function (todo_name, task_name) {
    if (!todo_name || !task_name) {
        console.error("Missing required parameters:", { todo_name, task_name });
        return;
    }

    task_name = $("<div/>").html(task_name).text();

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

                if (cur_frm) {
                    cur_frm.reload_doc();
                }

                $(".modal.show").modal("hide");

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

            let assignmentsHtml = "";
            const taskUsers =
                taskAssignments && task && task.name && taskAssignments[task.name] ? taskAssignments[task.name] : [];
            const maxAvatars = 3;

            const safeTaskName = task.name.replace(/['"\\]/g, function (c) {
                return "&#" + c.charCodeAt(0) + ";";
            });

            assignmentsHtml = `<div class="task-assignments" data-task="${safeTaskName}" onclick="handleTaskAssignment(this)">`;

            if (Array.isArray(taskUsers) && taskUsers.length > 0) {
                taskUsers.slice(0, maxAvatars).forEach((user) => {
                    if (user) {
                        try {
                            const userInitial = (user.charAt(0) || "").toUpperCase();

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

                if (taskUsers.length > maxAvatars) {
                    assignmentsHtml += `<div class="avatar-count" title="${
                        taskUsers.length - maxAvatars
                    } more users">+${taskUsers.length - maxAvatars}</div>`;
                }
            }

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

window.direct_remove_assign = function (taskName, todoName, buttonElement) {
    if (!taskName || !todoName) {
        console.error("Missing required parameters to remove assignment");
        return;
    }

    $(buttonElement).prop("disabled", true).html('<i class="fa fa-spinner fa-spin"></i>');

    frappe.call({
        method: "frappe.client.delete",
        args: {
            doctype: "ToDo",
            name: todoName,
        },
        callback: function (response) {
            $(buttonElement).prop("disabled", false).html(__("Remove"));

            if (!response.exc) {
                frappe.show_alert({
                    message: __("Assignment removed"),
                    indicator: "green",
                });

                $(buttonElement)
                    .closest(".assignee-item")
                    .slideUp(300, function () {
                        $(this).remove();

                        if ($(".assignee-item").length === 0) {
                            $(".assignee-list").html('<div class="text-muted">No assignees</div>');
                        }
                    });

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

                if (response.exc && response.exc.includes("Permission")) {
                    try_alternative_removal(taskName, todoName, buttonElement);
                }
            }
        },
    });
};

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
                frappe.show_alert({
                    message: __("Assignment removed (alternative method)"),
                    indicator: "green",
                });

                $(buttonElement)
                    .closest(".assignee-item")
                    .slideUp(300, function () {
                        $(this).remove();
                    });

                setTimeout(function () {
                    if (cur_frm) cur_frm.reload_doc();
                }, 1000);
            } else {
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
